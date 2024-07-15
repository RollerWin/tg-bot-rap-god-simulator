from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.dao import item as item_dao
from database.dao import user_item_association as user_item_association_dao
from database.dao import track as track_dao

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
      InlineKeyboardButton(text="Инвентарь", callback_data="inventory")
    ],
    [
        InlineKeyboardButton(text="Заработок", callback_data="work"),
        InlineKeyboardButton(text="Музыка", callback_data="music")
    ],
    [
        InlineKeyboardButton(text="Магазин", callback_data="shop"),
        InlineKeyboardButton(text="Донат", callback_data="donate")
    ],
    [
        InlineKeyboardButton(text="Казино", callback_data="casino")
    ],
    [
        InlineKeyboardButton(text="Тех.помощь", callback_data="help")
    ]
])

work_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Скам (Пригласить друга)", callback_data="invite_friend")],
    [InlineKeyboardButton(text="Сведение треков", callback_data="work_mixing_track")],
    [InlineKeyboardButton(text="Поработать в Макдоналдсе", callback_data="work_mcdonalds")],
    [InlineKeyboardButton(text="Грабёж", callback_data="work_robbery")],
    [InlineKeyboardButton(text="Нелегальные делишки", callback_data="work_cell_drugs")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

ready_to_work_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать работу", callback_data="go_to_work")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")],
])

donate_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1500", callback_data="donate_1500_2")],
    [InlineKeyboardButton(text="5000", callback_data="donate_5000_50")],
    [InlineKeyboardButton(text="10000", callback_data="donate_10000_100")],
    [InlineKeyboardButton(text="25000", callback_data="donate_25000_250")],
    [InlineKeyboardButton(text="125000", callback_data="donate_125000_1000")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

casino_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кости🎲", callback_data="dice")],
    [InlineKeyboardButton(text="Рулетка♦️♣️", callback_data="roulette")],
    [InlineKeyboardButton(text="Слоты🎰", callback_data="slots")],
    [InlineKeyboardButton(text="Назад", callback_data="main_button")]
])

play_again_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сыграть ещё раз", callback_data="play_again")],
    [InlineKeyboardButton(text="Назад", callback_data="main_button")]
])

item_info_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Купить", callback_data="buy_item")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

music_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Синглы", callback_data="single_music")],
    [InlineKeyboardButton(text="Альбомы", callback_data="album_music")],
    [InlineKeyboardButton(text="Лейблы", callback_data="label_music")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

single_music_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Создать сингл", callback_data="create_single_music")],
    [InlineKeyboardButton(text="Посмотреть мои синглы", callback_data="show_single_music")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

album_music_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Создать альбом", callback_data="create_album_music")],
    [InlineKeyboardButton(text="Посмотреть мои альбомы", callback_data="show_album_music")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

label_music_menu_for_empty_players = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Создать лейбл", callback_data="create_label")],
    [InlineKeyboardButton(text="Присоединиться к лейблу", callback_data="join_label")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])

label_music_menu_for_joined_players = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Создать лейбл", callback_data="create_label")],
    [InlineKeyboardButton(text="Присоединиться к лейблу", callback_data="join_label")],
    [InlineKeyboardButton(text="Посмотреть участников лейбла", callback_data="show_label_members")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])


label_music_menu_for_founders = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Создать лейбл", callback_data="create_label")],
    [InlineKeyboardButton(text="Присоединиться к лейблу", callback_data="join_label")],
    [InlineKeyboardButton(text="Посмотреть участников лейбла", callback_data="show_label_members")],
    [InlineKeyboardButton(text="Раздать лимитированный мерч", callback_data="label_giveaway")],
    [InlineKeyboardButton(text="Назад", callback_data="back_button")]
])


async def get_items_keyboard():
    items = await item_dao.get_items()
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_button"))
    for item in items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    return keyboard.adjust(2).as_markup()


async def get_user_items_keyboard(user_id):
    items = await user_item_association_dao.get_items(user_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_button"))
    for item in items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    return keyboard.adjust(1).as_markup()


async def get_payment_link_keyboard(link):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Оплатить", url=link))
    keyboard.add(InlineKeyboardButton(text="Получить!", callback_data="confirm_payment"))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_button"))
    return keyboard.adjust(1).as_markup()


async def get_user_single_music_keyboard(user_id):
    keyboard = InlineKeyboardBuilder()
    user_singles = await track_dao.get_tracks_by_author(user_id)
    for single in user_singles:
        keyboard.add(InlineKeyboardButton(text=single.track_name, callback_data=f'track_{single.id}'))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_button"))
    return keyboard.adjust(1).as_markup()
