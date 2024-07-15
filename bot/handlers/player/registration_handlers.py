from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database.dao import player as player_dao
from database.dao import stats_player as stats_player_dao
from bot.keyboards import registration_keyboards as reg_kb
from bot.keyboards import navigation_keyboards as nav_kb
from game_configuration import DefaultPlayerState
from game_configuration import DefaultGameConfiguration

player = Router()


class Registration(StatesGroup):
    username = State()
    skin_color = State()


@player.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Приветствуем в игре rap god!")
    player = await player_dao.add_player(message.from_user.id)
    if not player:
        await state.set_state(Registration.username)
        await message.answer("Введите имя вашего персонажа")
        refferer_id = str(message.text[7:])
        if str(refferer_id) != "":
            await state.update_data(bonus_balance=int(DefaultGameConfiguration.REFFERAL_BONUS_BALANCE))
            await state.update_data(bonus_fame=int(DefaultGameConfiguration.REFFERAL_BONUS_FAME))
            await state.update_data(bonus_respect=int(DefaultGameConfiguration.REFFERAL_BONUS_RESPECT))
            await stats_player_dao.edit_stats_player_by_refferal_code(int(refferer_id),
                                                                      int(DefaultGameConfiguration.REFFERAL_BONUS_BALANCE),
                                                                      int(DefaultGameConfiguration.REFFERAL_BONUS_FAME),
                                                                      int(DefaultGameConfiguration.REFFERAL_BONUS_RESPECT)
                                                                      )
    else:
        current_player = await player_dao.get_player(message.from_user.id)
        await message.answer(await write_info(current_player), reply_markup=nav_kb.main_menu)


@player.message(Registration.username)
async def register_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.update_data(tg_id=message.from_user.id)
    await state.set_state(Registration.skin_color)
    await message.answer("Введите цвет кожи вашего персонажа",
                         reply_markup=reg_kb.skin_color)


@player.callback_query(Registration.skin_color, F.data == "back_button")
async def change_username(call: CallbackQuery, state: FSMContext):
    await state.update_data(username="")
    await state.set_state(Registration.username)
    await call.message.edit_text("Введите имя вашего персонажа")


@player.callback_query(Registration.skin_color)
async def register_skin_color(call: CallbackQuery, state: FSMContext):
    skin_color_type = int(call.data.split('_')[2])
    await state.update_data(skin_color=skin_color_type)
    info = await state.get_data()

    bonus_balance = info.get("bonus_balance", 0)
    bonus_fame = info.get("bonus_fame", 0)
    bonus_respect = info.get("bonus_respect", 0)

    await player_dao.edit_player(info["tg_id"], info["username"])
    current_player = await player_dao.get_player(info["tg_id"])
    await stats_player_dao.add_stats_player(skin_color_type,
                                            info["tg_id"],
                                            bonus_balance,
                                            bonus_fame,
                                            bonus_respect
                                            )
    await call.answer("Вы выбрали цвет кожи!")
    await call.message.edit_text(f"Вы успешно зарегистрировали персонажа!\n" +
                                 await write_info(current_player),
                                 reply_markup=nav_kb.main_menu
                                 )
    await state.clear()


async def write_info(player):
    player_stats = await stats_player_dao.get_stats_player(player.tg_id)
    if player_stats.skin_color == DefaultPlayerState.WHITE_SKIN_COLOR_INDEX:
        skin_color = "белый"
    else:
        skin_color = "черный"

    text = (f"Добро пожаловать, {player.username} !\n\n"
            f"Цвет кожи: {skin_color}\n"
            f"Баланс: {player_stats.balance}\n"
            f"Законопослушность: {player_stats.criminal_rate}/100\n"
            f"Известность: {player_stats.fame}\n"
            f"Респект: {player_stats.respect}/100\n"
            f"Статус: {player_stats.status}\n")
    return text
