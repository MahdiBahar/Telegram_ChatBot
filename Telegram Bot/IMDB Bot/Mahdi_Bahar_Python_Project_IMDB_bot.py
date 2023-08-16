# IMDB Telegram bot Project
# Programmer: Mahdi Bahar


# import part
import requests
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, \
    InputMediaPhoto
import time
from telegram.ext.utils.promise import logger
from dotenv import dotenv_values

values = dotenv_values('.env')
print(values)


API_key_IMDB = '' #Enter API key getting from IMDB website


# API_KEY from Telegram bot

API_KEY_Tel= '' #Enter your API KEY from Telegram

updater = Updater(API_KEY_Tel)
dispatcher = updater.dispatcher


# Start Function
def start(update, context):
    msg = """"Hi 👋, Welcome to my IMDB searching Bot. To know what I can do, please check /help.
    """
    update.message.reply_text(msg)


# Help Function
def help(update, context):
    msg = """I can search any movies in IMDB 😊. For using this ability, please use /tools command.
✳️ Moreover, if the bot didn't response well, please start it again.
✅  You can also access to the all commands in  the left menu.
    """
    update.message.reply_text(msg)


# Tools Function
def tools(update, context):
    msg = '🖍️ Choose a tool'
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌏 Search movie", switch_inline_query_current_chat='')],
            # [InlineKeyboardButton("start", callback_data='back_to_start')]
        ]
    )
    update.message.reply_text(msg, reply_markup=keyboard)


# Searching title of movie and get list of them
def inline_search_movies(update, context):
    try:
        query = update.inline_query.query
        url = f"https://imdb-api.com/en/API/SearchMovie/{API_key_IMDB}/{query}"

        response = requests.get(url).json()
        results = []

        for movie in response['results']:
            results.append(
                InlineQueryResultArticle(
                    id=movie['id'],
                    title=movie['title'],
                    description=movie['description'],
                    thumb_url=movie['image'],
                    input_message_content=InputTextMessageContent(movie['id'])

                )

            )
        update.inline_query.answer(results)
    except Exception as exp:  # also could be "except TelegramError as exp"
        if str(exp) == 'Query is too old and response timeout expired or query id is invalid':
            logger.info('Query is too old and response timeout expired or query id is invalid')
            # ignoring this error:
            return
        # report the error otherwise:
        logger.error(f'Error while send_chart: {exp}')


# Report the error to the user
# def report_error(update, context):
#     msg = """SOMETHING WRONG!!!!!. Please wait for ew seconds.
#              If the problem is still going, so please start again the bot.
#                 """
#     update.message.reply_text(msg)

# Showing the details of movie
def display_movie_details(update, context):
    movie_id = update.message.text
    message_id = update.message.message_id
    chat_id = update.message.chat_id
    try:
        url = f"https://imdb-api.com/en/API/Title/{API_key_IMDB}/{movie_id}"

        response = requests.get(url).json()

        details = (
            f"""❇️ Title: {response['fullTitle']}

❇️ Type: {response['type']}

❇️ Genres: {response['genres']}

❇️ Rating: {response['imDbRating']}

❇️ Year: {response['year']}

❇️ Release Date: {response['releaseDate']}

❇️ Language: {response['languages']}

❇️ Duration: {response['runtimeStr']}

❇️ Directors: {response['directors']}

❇️ Stars: {response['stars']}

❇️ Awards: {response['awards']}

❇️ Abstract: {response['plot']}

            """
        )
        trailer_url = f"https://imdb-api.com/en/API/Trailer/{API_key_IMDB}/{movie_id}"

        trailer_response = requests.get(trailer_url).json()
        print('trailer_response', trailer_response)
        trailer_link = trailer_response.get("link")
        print('trailer_link', trailer_link)
        markup = [
            [
                InlineKeyboardButton("📸 View Images", callback_data=f"view_images:{movie_id}:{response['fullTitle']}"),
                InlineKeyboardButton("📽 Watch Trailer", url=trailer_link) if trailer_link else \
                    InlineKeyboardButton("😔 Trailer not available", callback_data="trailer_not_available")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(markup)
        update.message.reply_photo(photo=response["image"], caption=details, reply_markup=reply_markup,
                                   parse_mode="Markdown")

        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as exp:  # also could be "except TelegramError as exp"
        if str(exp) == 'Query is too old and response timeout expired or query id is invalid':
            logger.info('Query is too old and response timeout expired or query id is invalid')
            # ignoring this error:
            return
        # report the error otherwise:
        logger.error(f'Error while send_chart: {exp}')


# Define callback query
def handle_callback_query(update, context):
    query = update.callback_query
    data = query.data
    # print(query)
    # user_id= query.from_user.id
    print(data)
    try:
        if data.startswith("view_images:"):

            _, movie_id, movie_title = data.split(":", 2)

            print('movie ID', movie_id)
            print('movie title', movie_title)

            images_url = f"https://imdb-api.com/en/API/Images/{API_key_IMDB}/{movie_id}"
            # print('url images',images_url)
            images_response = requests.get(images_url).json()
            # print(images_response)
            image_items = images_response.get("items")[:10]

            if image_items:
                media_group = [InputMediaPhoto(media=item["image"]) for item in image_items]
                query.bot.send_media_group(chat_id=query.message.chat_id, media=media_group)
            else:
                query.answer("There is no image for this movie")

            trailer_url = f"https://imdb-api.com/en/API/Trailer/{API_key_IMDB}/{movie_id}"

            trailer_response = requests.get(trailer_url).json()
            print('trailer_response', trailer_response)
            trailer_link = trailer_response.get("linkEmbed")
            print(' trailer_link', trailer_link)
            markup = [
                [
                    InlineKeyboardButton("📽️ Watch Trailer", url=trailer_link) if trailer_link else \
                        InlineKeyboardButton("😔 Trailer not available", callback_data="trailer_not_available")
                ],
                # [
                #     InlineKeyboardButton("⬅️ back to tools", callback_data="back_to_tools")]
            ]

            reply_markup = InlineKeyboardMarkup(markup)
            query.message.reply_text(f"*{movie_title}* Movie Images", reply_markup=reply_markup, parse_mode="Markdown")
        # elif data.startswith("back_to_tools"):
        # dispatcher.add_handler(CommandHandler("tools", tools))
        else:
            pass

    except Exception as exp:  # also could be "except TelegramError as exp"
        if str(exp) == 'Query is too old and response timeout expired or query id is invalid':
            logger.info('Query is too old and response timeout expired or query id is invalid')
            # ignoring this error:
            return
        # report the error otherwise:
        logger.error(f'Error while send_chart: {exp}')


# Define Dispatchers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("tools", tools))

dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
dispatcher.add_handler(InlineQueryHandler(inline_search_movies))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, display_movie_details))

# Running the program
# while True:
#     try:
#         updater.start_polling()
#     except Exception:
#         time.sleep(10)
updater.start_polling()
updater.idle()