import asyncio
import random

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards import navigation_keyboards as nav_kb
from bot.keyboards import utility_keyboards as util_kb
from bot.handlers.player.registration_handlers import write_info
from database.dao import item as item_dao
from database.dao import player as player_dao
from database.dao import user_item_association as user_item_association_dao
from database.dao import stats_player as stats_player_dao
from game_configuration import DefaultGameConfiguration
from game_configuration import WorkConfiguration as w_config
from game_configuration import DefaultItems as di

menu = Router()


class Shop(StatesGroup):
    item = State()
    purchase = State()


class Work(StatesGroup):
    type = State()
    work_mcdonalds = State()
    work_mixing_track = State()


@menu.callback_query(F.data == "shop")
async def choose_shop(call: CallbackQuery, state: FSMContext):
    await state.set_state(Shop.item)
    await call.message.edit_text("Товары, представленные в магазине: ",
                                 reply_markup=await nav_kb.get_items_keyboard())


@menu.callback_query(Shop.item, F.data == "back_button")
async def reset_shop(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@menu.callback_query(Shop.item, F.data.startswith("item_"))
async def choose_item(call: CallbackQuery, state: FSMContext):
    await state.set_state(Shop.purchase)
    selected_item_id = int(call.data.split("_")[1])
    await state.update_data(item_id=selected_item_id)
    selected_item = await item_dao.get_item(selected_item_id)
    await call.answer("Вы выбрали: " + selected_item.name)
    await call.message.edit_text(f"Название: {selected_item.name}\n"
                                 f"Описание: {selected_item.description}\n\n"
                                 f"Цена: {selected_item.price}",
                                 reply_markup=nav_kb.item_info_keyboard)


@menu.callback_query(Shop.purchase, F.data == "back_button")
async def reset_purchase(call: CallbackQuery, state: FSMContext):
    await state.set_state(Shop.item)
    await state.update_data(item_id=None)
    await call.message.edit_text("Товары, представленные в магазине: ",
                                 reply_markup=await nav_kb.get_items_keyboard())


@menu.callback_query(Shop.purchase, F.data == "buy_item")
async def buy_item(call: CallbackQuery, state: FSMContext):
    info = await state.get_data()
    player = await player_dao.get_player(call.from_user.id)
    item = await item_dao.get_item(int(info["item_id"]))
    stats_player = await stats_player_dao.get_stats_player(player.tg_id)
    if stats_player.balance < item.price:
        await call.answer("Недостаточно средств!")
    else:
        await user_item_association_dao.add_association(player.id, item.id)
        await stats_player_dao.spend_money(player.tg_id, item.price)
        await call.answer("Вы купили: " + item.name + " !")
        await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@menu.callback_query(F.data == "work")
async def choose_work(call: CallbackQuery, state: FSMContext):
    await state.set_state(Work.type)
    await call.message.edit_text("Чем займёмся сегодня?",
                                 reply_markup=nav_kb.work_menu)


@menu.callback_query(Work.type, F.data == "back_button")
async def reset_work(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@menu.callback_query(Work.type, F.data == "invite_friend")
async def invite_friend(call: CallbackQuery):
    await call.answer("Вы выбрали: пригласить друга")
    player = await player_dao.get_player(call.from_user.id)
    print(await player_dao.get_player(call.from_user.id))
    await call.message.edit_text(f"Отлично! Пригласи своего друга по этой ссылке и получишь бонусы :)\n\n"
                                 f"https://t.me/{DefaultGameConfiguration.BOT_NICKNAME}?start={player.tg_id}",
                                 reply_markup=util_kb.to_main_menu_keyboard)


@menu.callback_query(Work.type, F.data == "work_mcdonalds")
async def choose_work_mcdonalds(call: CallbackQuery, state: FSMContext):
    await state.set_state(Work.work_mcdonalds)
    await call.answer("Вы выбрали работу в McDonalds!")
    await call.message.edit_text(f"Вы хотите пойти работать в McDonalds?\n"
                                 f"Время работы: {w_config.MCDONALDS_WORK_TIME} секунд\n"
                                 f"Вы заработаете: {w_config.MCDONALDS_REWARD_MONEY}\n"
                                 f"И повысите законопослушность на: {w_config.MCDONALDS_CRIMINAL_RATE_DOWNGRADE}\n\n"
                                 f"Это время вы не сможете ни с чем больше взаимодействовать."
                                 f"Вы согласны?", reply_markup=nav_kb.ready_to_work_menu)


@menu.callback_query(Work.work_mcdonalds, F.data == "go_to_work")
async def go_to_work_mcdonalds(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Вы выбрали: McDonalds\n\n"
                                 "Что ж, работа нелёгкая, но...зато честная\n\n"
                                 f"Осталось работать: {w_config.MCDONALDS_WORK_TIME} секунд")

    await asyncio.sleep(w_config.MCDONALDS_WORK_TIME)
    await stats_player_dao.add_money(call.from_user.id, w_config.MCDONALDS_REWARD_MONEY)
    await stats_player_dao.added_criminal_rate(call.from_user.id, w_config.MCDONALDS_CRIMINAL_RATE_DOWNGRADE)

    await state.set_state(Work.type)
    await call.message.edit_text("Ваша смена в макдаке окончена\n"
                                 "Чем займёмся сегодня?",
                                 reply_markup=nav_kb.work_menu)


@menu.callback_query(Work.work_mcdonalds, F.data == "back_button")
async def reset_work_mcdonalds(call: CallbackQuery, state: FSMContext):
    await state.set_state(Work.type)
    await call.message.edit_text("Чем займёмся сегодня?",
                                 reply_markup=nav_kb.work_menu)


@menu.callback_query(Work.type, F.data == "work_mixing_track")
async def choose_work_mixing_track(call: CallbackQuery, state: FSMContext):
    await state.set_state(Work.work_mixing_track)
    await call.answer("Вы выбрали сводить треки для исполнителей!")
    await call.message.edit_text(f"Вы хотите сводить треки?\n"
                                 f"Время работы: {w_config.MIXING_TRACK_TIME} секунд\n"
                                 f"Выплата будет зависеть от того, насколько сильно трек понравится клиенту\n"
                                 f"Вероятность довольного клиента зависит от вашей славы и качественного оборудования"
                                 f"В случае успеха, вы повышаете свою славу на {w_config.MIXING_TRACK_FAME_INCREASE} "
                                 f"и уважение {w_config.MIXING_TRACK_RESPECT_INCREASE}\n\n"
                                 f"Это время вы не сможете ни с чем больше взаимодействовать."
                                 f"Вы согласны?", reply_markup=nav_kb.ready_to_work_menu)


@menu.callback_query(Work.work_mixing_track, F.data == "go_to_work")
async def go_to_work_mixing_track(call: CallbackQuery):
    await call.message.edit_text("Вы выбрали: сведение треков!\n\n"
                                 "Все с этого начинали\n\n"
                                 f"Осталось работать: {w_config.MIXING_TRACK_TIME} секунд")

    await asyncio.sleep(w_config.MIXING_TRACK_TIME)
    current_probability = w_config.DEFAULT_PROBABILITY_TO_SUCCESS
    if await user_item_association_dao.is_user_got_item(call.from_user.id, di.SPEAKER):
        current_probability += di.SPEAKER_PROBABILITY_INCREASE
    if await user_item_association_dao.is_user_got_item(call.from_user.id,  di.PC):
        current_probability += di.PC_PROBABILITY_INCREASE

    print(current_probability)

    success = random.random() < current_probability

    if success:
        final_probability_number = current_probability
        earnings = 300 * final_probability_number
        fame_increase = w_config.MIXING_TRACK_FAME_INCREASE
        respect_increase = w_config.MIXING_TRACK_RESPECT_INCREASE

        await stats_player_dao.add_money(call.from_user.id, earnings)
        await stats_player_dao.add_fame(call.from_user.id, fame_increase)
        await stats_player_dao.add_respect(call.from_user.id, respect_increase)

        await call.message.edit_text(f"Вы успешно свели трек!\n\n"
                                     f"Вы заработали {earnings} монет.\n"
                                     f"Ваша слава увеличилась на {fame_increase}.\n"
                                     f"Ваше уважение увеличилось на {respect_increase}.\n"
                                     f"Ваш текущий баланс: {await stats_player_dao.get_balance(call.from_user.id)}",
                                     reply_markup=util_kb.back_keyboard)
    else:
        await stats_player_dao.add_respect(call.from_user.id, -w_config.MIXING_TRACK_RESPECT_INCREASE)
        await call.message.edit_text(
            "К сожалению, клиенту не понравился ваш трек. "
            "Вы не получили никаких вознаграждений и у вас упала репутация.",
            reply_markup=util_kb.back_keyboard)


@menu.callback_query(Work.work_mixing_track, F.data == "back_button")
async def reset_work_mixing_track(call: CallbackQuery, state: FSMContext):
    await state.set_state(Work.type)
    await call.message.edit_text("Чем займёмся сегодня?",
                                 reply_markup=nav_kb.work_menu)


@menu.callback_query(Work.type, F.data == "work_robbery")
async def choose_work_robbery(call: CallbackQuery, state: FSMContext):
    player_id = call.from_user.id
    if (await user_item_association_dao.is_user_got_item(player_id, di.PISTOL) or
            await user_item_association_dao.is_user_got_item(player_id, di.LIL_KNIFE)):

        await stats_player_dao.added_criminal_rate(player_id, w_config.ROBBERY_CRIMINAL_RATE_INCREASE)
        probability_to_catch = (1500 - 15 * await stats_player_dao.get_criminal_rate(player_id)) / 100**2

        is_not_catch = random.random() > probability_to_catch

        if is_not_catch:
            current_probability = w_config.DEFAULT_PROBABILITY_TO_SUCCESS
            if user_item_association_dao.is_user_got_item(player_id, di.PISTOL):
                current_probability += di.PISTOL_PROBABILITY_INCREASE
            if user_item_association_dao.is_user_got_item(player_id, di.LIL_KNIFE):
                current_probability += di.LIL_KNIFE_PROBABILITY_INCREASE

            success = random.random() < current_probability

            if success:
                await stats_player_dao.add_money(player_id, w_config.ROBBERY_REWARD_MONEY)
                await call.message.edit_text("Ограбление прошло успешно!",
                                             reply_markup=util_kb.back_keyboard)
            else:
                await call.message.edit_text("Ограбление провалено!\n"
                                             "Хорошо, что вас не поймали полицейские",
                                             reply_markup=util_kb.back_keyboard)
        else:
            await user_item_association_dao.remove_illegal_associations(player_id)
            added_text = ""
            player_balance = await stats_player_dao.get_balance(player_id)
            if player_balance < w_config.ROBBERY_MONEY_PENALTY:
                await stats_player_dao.spend_money(player_id, player_balance)
                added_text = ("Да вы ещё и такой неудачник, что у вас даже не хватило денег на штраф. "
                              "Теперь у вас просто нет денег")
            else:
                await stats_player_dao.spend_money(player_id, w_config.ROBBERY_MONEY_PENALTY)

            await call.message.edit_text("Ограбление провалено!\n"
                                         "С вас взяли штраф и изъяли все запрещённые вещи!\n"
                                         f"{added_text}"
                                         "Теперь вы сидите в тюрьме!\n"
                                         f"Срок: {w_config.ROBBERY_TIME_PENALTY}")
            await asyncio.sleep(w_config.ROBBERY_TIME_PENALTY)
            await call.message.edit_text("Ограбление провалено!\n"
                                         "С вас взяли штраф и изъяли все запрещённые вещи!\n"
                                         f"{added_text}\n"
                                         "Вы сидите в тюрьме!\n"
                                         f"Срок: {w_config.ROBBERY_TIME_PENALTY} секунд",
                                         reply_markup=util_kb.back_keyboard)
    else:
        await call.answer("Вы не можете грабить! У вас даже оружия нет!")


@menu.callback_query(Work.type, F.data == "back_button")
async def reset_work_mixing_track(call: CallbackQuery, state: FSMContext):
    await state.set_state(Work.type)
    await call.message.edit_text("Чем займёмся сегодня?",
                                 reply_markup=nav_kb.work_menu)


@menu.callback_query(F.data == "main_button")
async def to_main_menu(call: CallbackQuery):
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)
