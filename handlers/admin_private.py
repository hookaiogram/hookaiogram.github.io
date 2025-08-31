from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_product,
    orm_get_product,
    orm_get_products,
    orm_update_product,
)

from filters.chat_types import ChatTypeFilter, IsAdmin

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Ввести индекс",
    "Изменить индекс",
    placeholder="Выберите действие",
    sizes=(2,),
)


class AddProduct(StatesGroup):
    # Шаги состояний
    index = State()


    product_for_change = None

    texts = {
        "AddProduct:index": "Введите название заново:",

    }


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Изменить индекс")
async def starring_at_product(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer(
            f"{product.index}",
            reply_markup=get_callback_btns(
                btns={
                    #"Удалить": f"delete_{product.id}",
                    "Изменить": f"change_{product.id}",
                }
            ),
        )
    await message.answer("ОК")




# FSM:

# Становимся в состояние ожидания ввода name
@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]

    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите индекс", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.index)


# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Ввести индекс")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите индекс", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.index)





# Ловим данные для состояние name и потом меняем состояние на description
@admin_router.message(AddProduct.index, or_f(F.text, F.text == "."))
async def add_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == ".":
        await state.update_data(index=AddProduct.product_for_change.index)
    else:

        await state.update_data(index=message.text)
        data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer("Индекс изменен", reply_markup=ADMIN_KB)
        await state.clear()

    except ImportError as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программеру, он опять денег хочет",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddProduct.product_for_change = None
