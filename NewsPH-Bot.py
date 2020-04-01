import json
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import feedparser
from bs4 import BeautifulSoup
import random
from functools import wraps
from telegram import ChatAction


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


@send_typing_action
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="NewsPH_Bot has been created to provide you with the latest news updates from the most popular news sources in the Philippines.",
    )


def get_entries():
    url = "https://rss.app/feeds/06baSi0bagPEqNTP.xml"
    NewsFeed = feedparser.parse(url)
    entries = NewsFeed.entries
    return entries


def get_headline(entry):
    try:
        headline = entry.title
        return headline
    except AttributeError:
        return ""


def get_image(entry):
    try:
        thisdict = entry.media_content[0]
        media = thisdict["url"]
        return media
    except AttributeError:
        return ""


def get_summary(entry):
    try:
        html = entry.summary
        parsed_html = BeautifulSoup(html, features="html.parser")
        summary = parsed_html.find("div").text
        if summary == "":
            src = parsed_html.find("iframe").get("src")
            summary = src
        return summary
    except AttributeError:
        return ""


def get_author(entry):
    try:
        author = entry.author
        return author
    except AttributeError:
        return ""


def get_date(entry):
    try:
        date = entry.published
        return date
    except AttributeError:
        return ""


def get_title(entry):
    news_content = get_headline(entry)
    return news_content


def get_media(entry):
    news_content = get_image(entry)
    return news_content


def get_text(entry):
    news_content = (
        get_summary(entry) + "\n" + get_author(entry) + "\n" + get_date(entry)
    )
    return news_content


@send_typing_action
def send_top_entry(update, context):
    entries = get_entries()
    entry = entries[0]
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_title(entry))
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=get_media(entry))
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_text(entry))


@send_typing_action
def send_random_entry(update, context):
    entries = get_entries()
    number_of_entries = len(entries) - 1
    entry_index = random.randint(0, number_of_entries)
    entry = entries[entry_index]
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_title(entry))
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=get_media(entry))
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_text(entry))


@send_typing_action
def send_all_entries(update, context):
    entries = get_entries()
    for entry in entries:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=get_title(entry)
        )
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=get_media(entry))
        context.bot.send_message(chat_id=update.effective_chat.id, text=get_text(entry))


@send_typing_action
def send_number_of_entries(update, context):
    entries = get_entries()
    args = context.args
    if not args:
        args.append(1)
    if args[0] == "0":
        args[0] = "1"
    limit = int(args[0])
    for entry in entries[:limit]:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=get_title(entry)
        )
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=get_media(entry))
        context.bot.send_message(chat_id=update.effective_chat.id, text=get_text(entry))


def main():
    # Get token
    with open("Token.json") as tokens:
        dict_tokens = json.load(tokens)
    token = dict_tokens["NewsPH"]
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    # Logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # Command handlers
    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)
    news_handler = CommandHandler("news", send_top_entry)
    dispatcher.add_handler(news_handler)
    random_handler = CommandHandler("random", send_random_entry)
    dispatcher.add_handler(random_handler)
    read_handler = CommandHandler("read", send_number_of_entries)
    dispatcher.add_handler(read_handler)
    all_handler = CommandHandler("all", send_all_entries)
    dispatcher.add_handler(all_handler)
    # Start bot
    updater.start_polling()


if __name__ == "__main__":
    main()
