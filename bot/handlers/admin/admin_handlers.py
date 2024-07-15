from aiogram import Router, F, Bot
from aiogram.filters.command import Command
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database.dao import item as item_dao
from database.dao import player as player_dao
from database.dao import stats_player as stats_player_dao
from bot.keyboards import utility_keyboards as util_kb
from game_configuration import DefaultItems as di

admin = Router()


class AddItem(StatesGroup):
    name = State()
    description = State()
    price = State()


class Admin(Filter):
    def __init__(self):
        self.admins = [309437108, 447706035]

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins


@admin.message(Admin(), Command('create_default'))
async def create_default(message: Message):
    await item_dao.add_item(di.SPEAKER, di.SPEAKER_PRICE, di.SPEAKER_IS_LEGAL, di.SPEAKER_DESCRIPTION)
    await item_dao.add_item(di.PC, di.PC_PRICE, di.PC_IS_LEGAL, di.PC_DESCRIPTION)
    await item_dao.add_item(di.PISTOL, di.PISTOL_PRICE, di.PISTOL_IS_LEGAL, di.PISTOL_DESCRIPTION)
    await item_dao.add_item(di.LIL_KNIFE, di.LIL_KNIFE_PRICE, di.LIL_KNIFE_IS_LEGAL, di.LIL_KNIFE_DESCRIPTION)
    await message.answer("Предметы по умолчанию созданы!")


@admin.message(Command('create_item'))
async def create_item(message: Message, state: FSMContext):
    await state.set_state(AddItem.name)
    await message.answer("Введите название предмета:", reply_markup=util_kb.back_keyboard)


@admin.message(Command('show_players'))
async def show_players(message: Message):
    players = await player_dao.get_players()
    player_info = ""

    for player in players:
        stats_player = await stats_player_dao.get_stats_player(player.tg_id)
        player_info += f"Имя: {player.username}\n"
        player_info += f"ID: {player.tg_id}\n"
        player_info += f"Баланс: {stats_player.balance}\n"
        player_info += f"Уважение: {stats_player.respect}\n"
        player_info += f"Слава: {stats_player.fame}\n"
        player_info += f"цвет кожи: {stats_player.skin_color}\n"
        player_info += f"-------------------------------------\n"

    await message.answer(player_info)


@admin.callback_query(F.data == "back_button", AddItem.name)
async def reset_create_item(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Создание предмета отменено!")


@admin.message(AddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddItem.description)
    await message.answer("Введите описание предмета:", reply_markup=util_kb.back_keyboard)


@admin.callback_query(F.data == "back_button", AddItem.description)
async def reset_item_name(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddItem.name)
    await state.update_data(name="")
    await call.answer("Вы отменили название предмета!")
    await call.message.edit_text("Введите название предмета:", reply_markup=util_kb.back_keyboard)


@admin.message(AddItem.description)
async def add_item_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddItem.price)
    await message.answer("Введите стоимость предмета:", reply_markup=util_kb.back_keyboard)


@admin.callback_query(F.data == "back_button", AddItem.price)
async def reset_item_description(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddItem.description)
    await state.update_data(description="")
    await call.answer("Вы отменили описание предмета!")
    await call.message.edit_text("Введите описание предмета:", reply_markup=util_kb.back_keyboard)


@admin.message(Admin(), AddItem.price)
async def add_item_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    item = await state.get_data()
    await item_dao.add_item(item["name"], int(item["price"]), item["description"])
    await message.answer("Предмет добавлен!")
