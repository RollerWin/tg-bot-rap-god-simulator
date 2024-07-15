from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from game_configuration import DefaultPlayerState

skin_color = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='🙎🏾‍♂️', callback_data=f'skin_color_{DefaultPlayerState.BLACK_SKIN_COLOR_INDEX}'),
    ],
    [
        InlineKeyboardButton(text='🙎🏼‍♂️', callback_data=f'skin_color_{DefaultPlayerState.WHITE_SKIN_COLOR_INDEX}')
    ],
    [
        InlineKeyboardButton(text='Назад', callback_data='back_button')
    ]
])
