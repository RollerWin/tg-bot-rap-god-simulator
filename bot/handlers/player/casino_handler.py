import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards import navigation_keyboards as nav_kb
from bot.keyboards import utility_keyboards as utility_kb
from bot.handlers.player.registration_handlers import write_info
from database.dao import player as player_dao
from database.dao import stats_player as stats_player_dao
from database.dao import player_in_game as player_in_game_dao

from game_configuration import CasinoRules as cr

casino = Router()


class Casino(StatesGroup):
    select_game = State()
    play_game = State()


@casino.callback_query(F.data == "casino")
async def enter_casino(call: CallbackQuery, state: FSMContext):
    stats_player = await stats_player_dao.get_stats_player(call.from_user.id)
    if stats_player.respect < 10:
        await call.answer("Вы недостаточно статусны для входа в казино!")
    else:
        await state.set_state(Casino.select_game)
        await call.message.edit_text("Выберите игру в казино:", reply_markup=nav_kb.casino_menu)


@casino.callback_query(Casino.select_game, F.data == "main_button")
async def to_main_menu_from_casino(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@casino.callback_query(Casino.select_game, F.data == "dice")
async def play_dice(call: CallbackQuery, state: FSMContext):
    game_cost = cr.DICE_GAME_COST
    winnings = cr.DICE_REWARD
    game_code = cr.DICE_GAME_ID
    player_id = call.from_user.id

    if await stats_player_dao.get_balance(player_id) < game_cost:
        await call.answer("У вас недостаточно денег для игры!")
    else:
        opponent = await player_in_game_dao.get_player_in_game(1, player_id)
        print(opponent)

        if opponent is None:
            await call.message.edit_text("Игроки не найдены, начат поиск",
                                         reply_markup=utility_kb.back_keyboard)
            await player_in_game_dao.add_player_game(player_id, game_code)
        else:
            await state.set_state(Casino.play_game)
            opponent_id = opponent.tg_id
            await stats_player_dao.spend_money(player_id, game_cost)
            await stats_player_dao.spend_money(opponent_id, game_cost)

            opponent_result_msg = await call.bot.send_dice(chat_id=opponent_id, emoji='🎲')
            player_result_msg = await call.bot.send_dice(chat_id=player_id, emoji='🎲')

            opponent_result = opponent_result_msg.dice.value
            player_result = player_result_msg.dice.value

            if opponent_result > player_result:
                winner_id = opponent_id
                loser_id = player_id
            else:
                winner_id = player_id
                loser_id = opponent_id

            await asyncio.sleep(3)
            await stats_player_dao.add_money(winner_id, winnings)
            await player_in_game_dao.remove_player_in_game(opponent_id, 1)
            await call.bot.send_message(chat_id=winner_id, text=f"Вы выиграли  {winnings}!\n", reply_markup=nav_kb.play_again_keyboard)
            await call.bot.send_message(chat_id=loser_id, text=f"Вы проиграли!\n", reply_markup=nav_kb.play_again_keyboard)


@casino.callback_query(Casino.select_game, F.data == "back_button")
async def back_to_casino(call: CallbackQuery, state: FSMContext):
    await state.set_state(Casino.select_game)
    await player_in_game_dao.remove_player_in_game(call.from_user.id, 1)
    await call.message.edit_text("Выберите игру в казино:", reply_markup=nav_kb.casino_menu)


@casino.callback_query(Casino.select_game, F.data == "roulette")
async def play_roulette(call: CallbackQuery, state: FSMContext):
    game_cost = cr.ROULETTE_GAME_COST
    winnings = cr.ROULETTE_REWARD
    player_id = call.from_user.id

    await stats_player_dao.spend_money(player_id, game_cost)
    await stats_player_dao.add_money(player_id, winnings)
    await call.message.edit_text(f"Вы играете в рулетку и выиграли {winnings}!\n"
                                 f"Ваш баланс: {stats_player_dao.get_balance(player_id)}",
                                 reply_markup=nav_kb.play_again_keyboard)


@casino.callback_query(Casino.select_game, F.data == "slots")
async def play_slots(call: CallbackQuery, state: FSMContext):
    game_cost = cr.SLOTS_GAME_COST
    current_winnings = 0

    player_id = call.from_user.id

    if await stats_player_dao.get_balance(player_id) < game_cost:
        await call.answer("У вас недостаточно денег для игры!")
    else:
        await state.set_state(Casino.play_game)
        await stats_player_dao.spend_money(player_id, game_cost)
        message = await call.message.answer_dice(emoji='🎰')
        dice_value = message.dice.value
        print(dice_value)

        await asyncio.sleep(3)

        if dice_value in (1, 22, 43):
            current_winnings = cr.SLOTS_MIN_REWARD
        elif dice_value in (16, 32, 48):
            current_winnings = cr.SLOTS_MID_REWARD
        elif dice_value == 64:
            current_winnings = cr.SLOTS_MAX_REWARD

        if current_winnings != 0:
            await stats_player_dao.add_money(player_id, current_winnings)

        await call.message.answer(f"Вы играете в слоты и выиграли {current_winnings}!\n"
                                  f"Ваш баланс: { await stats_player_dao.get_balance(player_id)}",
                                  reply_markup=nav_kb.play_again_keyboard)


@casino.callback_query(Casino.play_game, F.data == "play_again")
async def play_again(call: CallbackQuery, state: FSMContext):
    await state.set_state(Casino.select_game)
    await call.message.edit_text("Выберите игру в казино:", reply_markup=nav_kb.casino_menu)


@casino.callback_query(Casino.play_game, F.data == "main_button")
async def to_main_menu_from_play_again(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)
