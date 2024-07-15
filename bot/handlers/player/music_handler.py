import asyncio
import random

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards import navigation_keyboards as nav_kb
from bot.keyboards import utility_keyboards as util_kb
from bot.handlers.player.registration_handlers import write_info
from database.dao import item as item_dao
from database.dao import player as player_dao
from database.dao import user_item_association as user_item_association_dao
from database.dao import stats_player as stats_player_dao
from database.dao import track as track_dao
from database.dao import label as label_dao
from database.dao import member as member_dao
from game_configuration import DefaultGameConfiguration
from game_configuration import MusicConfiguration as mc

music = Router()


class Music(StatesGroup):
    menu = State()
    sub_menu = State()
    show = State()
    show_details = State()
    single_create = State()
    label_create = State()


@music.callback_query(F.data == "music")
async def music_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.menu)
    await call.message.edit_text("Управление деятельностью", reply_markup=nav_kb.music_menu)


@music.callback_query(Music.menu, F.data == "back_button")
async def reset_music(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@music.callback_query(Music.menu, F.data == "single_music")
async def single_music_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.sub_menu)
    await call.message.edit_text("Надо же, юный гэнгста решил взглянуть в сторону синглов",
                                 reply_markup=nav_kb.single_music_menu)


@music.callback_query(Music.sub_menu, F.data == "back_button")
async def reset_single_music(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.menu)
    await call.message.edit_text("Управление деятельностью", reply_markup=nav_kb.music_menu)


@music.callback_query(Music.sub_menu, F.data == "show_single_music")
async def show_single_music_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.show)
    player_id = call.from_user.id
    await call.message.edit_text("Вот весь список синглов, написанных вами когда-либо",
                                 reply_markup=await nav_kb.get_user_single_music_keyboard(player_id))


@music.callback_query(Music.show, F.data == "back_button")
async def reset_show_single_music(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.sub_menu)
    await call.message.edit_text("Надо же, юный гэнгста решил взглянуть в сторону синглов",
                                 reply_markup=nav_kb.single_music_menu)


@music.callback_query(Music.show, F.data.startswith("track_"))
async def show_single_music_detail(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.show_details)
    track_id = call.data.split("_")[1]
    track = await track_dao.get_track_info(int(track_id))
    await call.message.edit_text(f"Название: {track.track_name}\n"
                                 f"Количество прослушиваний: {track.number_of_listeners}",
                                 reply_markup=util_kb.back_keyboard)


@music.callback_query(Music.show_details, F.data == "back_button")
async def reset_show_single_music_detail(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.show)
    player_id = call.from_user.id
    await call.message.edit_text("Вот весь список синглов, написанных вами когда-либо",
                                 reply_markup=await nav_kb.get_user_single_music_keyboard(player_id))


@music.callback_query(Music.sub_menu, F.data == "create_single_music")
async def create_single_music_callback(call: CallbackQuery, state: FSMContext):
    player_id = call.from_user.id
    player_money = await stats_player_dao.get_balance(player_id)

    if player_money < mc.MIN_MONEY_TO_CREATE_SINGLE:
        await call.answer("У вас недостаточно денег для создания сингла")
    else:
        await state.set_state(Music.single_create)
        await call.message.edit_text("Введите название сингла",
                                     reply_markup=util_kb.back_keyboard)


@music.callback_query(Music.single_create, F.data == "back_button")
async def reset_create_single_music(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.sub_menu)
    await call.message.edit_text("Надо же, юный гэнгста решил взглянуть в сторону синглов",
                                 reply_markup=nav_kb.single_music_menu)


@music.message(Music.single_create)
async def create_single_music(message: Message, state: FSMContext):
    await track_dao.add_track(message.from_user.id, message.text)
    await state.set_state(Music.menu)
    await message.answer("Сингл создан", reply_markup=nav_kb.music_menu)


@music.callback_query(Music.menu, F.data == "label_music")
async def single_music_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.sub_menu)
    player_id = call.from_user.id
    current_keyboard = nav_kb.label_music_menu_for_empty_players

    if await label_dao.is_user_founder(player_id):
        current_keyboard = nav_kb.label_music_menu_for_founders
    elif await member_dao.is_user_member(player_id):
        current_keyboard = nav_kb.label_music_menu_for_joined_players

    await call.message.edit_text("Добро пожаловать в высшую лигу!\nВ управление и присоединение к лейблам",
                                 reply_markup=current_keyboard)


@music.callback_query(Music.sub_menu, F.data == "create_label")
async def create_label_callback(call: CallbackQuery, state: FSMContext):
    player_id = call.from_user.id
    stats_player = await stats_player_dao.get_balance(player_id)

    if stats_player < mc.MONEY_TO_CREATE_LABEL:
        await call.answer("У вас недостаточно денег для создания лейбла")
    else:
        await state.set_state(Music.label_create)
        await call.message.edit_text("Введите название лейбла",
                                 reply_markup=util_kb.back_keyboard)


@music.callback_query(Music.label_create, F.data == "back_button")
async def reset_create_label(call: CallbackQuery, state: FSMContext):
    await state.set_state(Music.sub_menu)
    player_id = call.from_user.id
    current_keyboard = nav_kb.label_music_menu_for_empty_players

    if await label_dao.is_user_founder(player_id):
        current_keyboard = nav_kb.label_music_menu_for_founders
    elif await member_dao.is_user_member(player_id):
        current_keyboard = nav_kb.label_music_menu_for_joined_players
    await call.message.edit_text("Добро пожаловать в высшую лигу!\nВ управление и присоединение к лейблам",
                                 reply_markup=current_keyboard)


@music.message(Music.label_create)
async def create_label_music(message: Message, state: FSMContext):
    await label_dao.add_label(message.from_user.id, message.text)
    await state.set_state(Music.menu)
    await message.answer("Лейбл создан", reply_markup=nav_kb.music_menu)


async def update_number_of_listeners():
    tracks = await track_dao.get_all_tracks()

    if tracks:
        for track in tracks:
            player = await track_dao.get_author_by_track(track.id)
            stats_player = await stats_player_dao.get_stats_player(player.tg_id)
            listeners_growth = (mc.AVERAGE_GROWTH_LISTENERS_PER_HOUR *
                                (stats_player.fame / 100))

            player_reward = listeners_growth * mc.MONEY_PER_LISTENER
            await track_dao.increase_track_listeners(track.id, listeners_growth)
            await stats_player_dao.add_money(player.tg_id, player_reward)
