import string
import random
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from yoomoney import Quickpay, Client
from dotenv import load_dotenv

from bot.keyboards import navigation_keyboards as nav_kb
from bot.keyboards import utility_keyboards as util_kb
from bot.handlers.player.registration_handlers import write_info
from database.dao import player as player_dao
from database.dao import stats_player as stats_player_dao

payment = Router()
load_dotenv()


class Donate(StatesGroup):
    item = State()
    purchase = State()
    confirm = State()


@payment.callback_query(F.data == "donate")
async def menu_donate(call: CallbackQuery, state: FSMContext):
    await state.set_state(Donate.item)
    await call.answer("Вы перешли на страницу Доната!")
    await call.message.edit_text("Пополнение баланса на следующую сумму: ", reply_markup=nav_kb.donate_menu)


@payment.callback_query(Donate.item, F.data == "back_button")
async def reset_donate(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)


@payment.callback_query(Donate.item, F.data.startswith("donate_"))
async def buy_donate(call: CallbackQuery, state: FSMContext):
    await state.set_state(Donate.purchase)
    selected_donate_amount = int(call.data.split("_")[1])
    donate_amount_in_rubles = int(call.data.split("_")[2])

    letters_and_digits = string.ascii_lowercase + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, 10))

    await state.update_data(rand_string=rand_string)
    await state.update_data(selected_donate_amount=selected_donate_amount)
    quickpay = Quickpay(
        receiver='4100118683708376',
        quickpay_form='shop',
        targets=f'Оплата игровой валюты в количестве {selected_donate_amount} монет',
        paymentType='AB',
        sum=donate_amount_in_rubles,
        label=rand_string
    )

    await call.answer(f"Вы выбрали: {selected_donate_amount}")
    await call.message.edit_text(f"Количество валюты: {selected_donate_amount}\n"
                                 f"Стоимость: {donate_amount_in_rubles} рублей\n",
                                 reply_markup=await nav_kb.get_payment_link_keyboard(quickpay.redirected_url))


@payment.callback_query(Donate.purchase, F.data == "back_button")
async def cancel_donate(call: CallbackQuery, state: FSMContext):
    await state.clear()
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player),
                                 reply_markup=nav_kb.main_menu)


@payment.callback_query(Donate.purchase, F.data == "confirm_payment")
async def confirm_donate(call: CallbackQuery, state: FSMContext):
    client = Client(os.getenv("YOOMONEY_ACCESS_TOKEN"))
    info = await state.get_data()
    history = client.operation_history(label=str(info['rand_string']))
    try:
        operation = history.operations[-1]
        if operation.status == 'success':
            await stats_player_dao.add_money(call.from_user.id, int(info['selected_donate_amount']))
            await call.message.edit_text("Успешно оплачено!",
                                         reply_markup=util_kb.to_main_menu_keyboard)
        else:
            await call.answer("Ошибка оплаты!")
        await state.clear()
    except Exception as e:
        await call.answer("Ошибка оплаты!")


@payment.callback_query(F.data == "main_button")
async def to_main_menu(call: CallbackQuery):
    player = await player_dao.get_player(call.from_user.id)
    await call.message.edit_text(await write_info(player), reply_markup=nav_kb.main_menu)
