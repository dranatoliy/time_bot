import asyncio
import json
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from time_messenger import AsyncDriver
from TOKEN_BOT import TOKEN_BOT, LOGIN_SHARE, PASS_SHARE
from validation import validation_number, is_valid_date, is_valid_date_new, is_valid_summa
from helik import zapros_popolnenia, zapros_popolnenia_date
from datetime import datetime
import tinkoffpy as tf

driver_config = {
    # as time-messenger lib does not provide a proper way to pass
    # websocket specific url, we have to set "ws.time.tinkoff.ru"
    # as base url for both WS and HTTP requests
    "url": "ws.time.tinkoff.ru",
    "scheme": "https",
    "port": 443,
    "token": TOKEN_BOT,
    "debug": False,
}
channel_id = 'zstuqejwjpdj3gh6mqjzez5hda'


# zstuqejwjpdj3gh6mqjzez5hda
# yx5fheddjt8xzcio1rhaafci6w канал мой
async def init_background_websocket():
    time_driver = AsyncDriver(options=driver_config)

    async with time_driver:
        await time_driver.login()

        websocket_coro = time_driver.init_websocket(event_handler)
        asyncio.create_task(websocket_coro)


async def event_handler(event_message):
    time_driver = AsyncDriver(options=driver_config)
    #
    async with time_driver:
        await time_driver.login()

        event_data = json.loads(event_message)

        if "event" in event_data and event_data["event"] == "posted":
            post_data = json.loads(event_data["data"]["post"])
            print(event_data)
            print(time_driver.client.userid)

            if not post_data["user_id"] == time_driver.client.userid:
                direct_channel = await time_driver.channels.create_direct_message_channel(
                    options=[
                        time_driver.client.userid,
                        post_data["user_id"],
                    ]
                )
            if post_data["channel_id"] == channel_id:
                print(post_data)

                if post_data['root_id'] == '' and 'Проверка пополнения' in post_data['message']:

                    zapros = str(post_data['message']).split('\n')
                    number = zapros[5]
                    data_from = zapros[7]
                    data_to = zapros[9]
                    if validation_number(number) == True and is_valid_date(data_from, data_to) == True:
                        date_object_from = datetime.strptime(data_from, '%d.%m.%Y')
                        date_object_to = datetime.strptime(data_to, '%d.%m.%Y')

                        df = zapros_popolnenia(str(date_object_from.date()), str(date_object_to.date()), number)
                        if df.empty:
                            await time_driver.posts.create_post(
                                options={
                                    "channel_id": channel_id,
                                    "message": f'Попытки пополнения не найдены',
                                    "root_id": post_data['id'],
                                }
                            )
                        else:
                            await time_driver.posts.create_post(
                                options={
                                    "channel_id": channel_id,
                                    "message": f'```\n{df.to_string()}\n```',
                                    "root_id": post_data['id'],
                                }
                            )
                    elif validation_number(number) != True:
                        await time_driver.posts.create_post(
                            options={
                                "channel_id": channel_id,
                                "message": validation_number(number),
                                "root_id": post_data['id'],
                            }
                        )
                    elif is_valid_date(data_from, data_to) != True:
                        await time_driver.posts.create_post(
                            options={
                                "channel_id": channel_id,
                                "message": is_valid_date(data_from, data_to),
                                "root_id": post_data['id'],
                            }
                        )
                elif post_data['root_id'] == '' and 'Выгрузка данных по пополнениям' in post_data['message']:

                    zapros = str(post_data['message']).split('\n')
                    data_from = zapros[5]
                    summa = zapros[7]
                    user = (zapros[0]).split('@')[1]
                    print(data_from, summa)

                    if is_valid_date_new(data_from) == True and is_valid_summa(summa) == True:
                        date_object_from = datetime.strptime(data_from, '%d.%m.%Y')

                        df = zapros_popolnenia_date(str(date_object_from.date()), summa)

                        link = tf.cloud_upload(df,
                                               f'Выгрузка пополнений/{user}.csv',
                                               LOGIN_SHARE,
                                               PASS_SHARE,
                                               "share.tinkoff.ru",
                                               "cp1251")

                        await time_driver.posts.create_post(
                            options={
                                "channel_id": channel_id,
                                "message": f'[Выгружена 1000 пополнений]({link})',
                                "root_id": post_data['id'],
                            }
                        )

                    elif is_valid_date_new(data_from) != True:
                        await time_driver.posts.create_post(
                            options={
                                "channel_id": channel_id,
                                "message": is_valid_date_new(data_from),
                                "root_id": post_data['id'],
                            }
                        )

                    elif is_valid_summa(summa) != True:
                        await time_driver.posts.create_post(
                            options={
                                "channel_id": channel_id,
                                "message": is_valid_summa(summa),
                                "root_id": post_data['id'],
                            }
                        )

                await time_driver.reactions.create_reaction(
                    options={
                        "user_id": '6jcgymry5pgufmdrpzkecpxfkr',
                        "post_id": post_data['id'],
                        "emoji_name": 'white_check_mark',
                        'create_at': 0
                    }
                )


async def index_route(request):
    return HTMLResponse("hello there")


if __name__ == "__main__":
    """
    Serves as a regular ASGI server with one endpoint
    and background websocket connection with echo reply handler
    """

    # logging.basicConfig(level=logging.DEBUG)

    app = Starlette(
        routes=[Route("/", index_route)],
        on_startup=[init_background_websocket],
    )

    uvicorn.run(app)
