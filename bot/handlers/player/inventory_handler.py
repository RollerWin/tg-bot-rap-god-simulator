import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards import navigation_keyboards as nav_kb
from bot.handlers.player.registration_handlers import write_info
from bot.keyboards import utility_keyboards as util_kb
from bot.handlers.player.registration_handlers import write_info
from database.dao import item as item_dao
from database.dao import player as player_dao
from database.dao import user_item_association as user_item_association_dao
from database.dao import stats_player as stats_player_dao
from game_configuration import DefaultGameConfiguration
from game_configuration import WorkConfiguration as w_config

inventory = Router()


class Inventory(StatesGroup):
    look = State()
    item_description = State()


@inventory.callback_query(F.data == "inventory")
async def inventory_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Inventory.look)
    await call.answer("Вы зашли в свой инвентарь!")
    await call.message.edit_text("Ваши предметы: ",
                                 reply_markup=await nav_kb.get_user_items_keyboard(call.from_user.id))


@inventory.callback_query(Inventory.look, F.data == "back_button")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@inventory.callback_query(Inventory.look, F.data.startswith("item_"))
async def look_item(call: CallbackQuery, state: FSMContext):
    await state.set_state(Inventory.item_description)
    item_id = int(call.data.split("_")[1])
    item = await item_dao.get_item(item_id)
    await call.message.edit_text(f"{item.name}\n{item.description}", reply_markup=util_kb.back_keyboard)


@inventory.callback_query(Inventory.item_description, F.data == "back_button")
async def back_to_inventory_list(call: CallbackQuery, state: FSMContext):
    await state.set_state(Inventory.look)
    await call.answer("Вы зашли в свой инвентарь!")
    await call.message.edit_text("Ваши предметы: ",
                                 reply_markup=await nav_kb.get_user_items_keyboard(call.from_user.id))
