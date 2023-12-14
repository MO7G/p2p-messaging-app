import re
import webbrowser


def display_message(username, message, is_current_user):
    """
    Formats and displays a message with basic text formatting, hyperlinks, and color.
    """
    # Apply text formatting
    formatted_message = parse_bold(message)
    formatted_message = parse_italics(formatted_message)

    # Color hyperlinks in blue
    formatted_message = display_hyperlinks(formatted_message)

    # Apply color based on user
    colored_username = color_green(username) if is_current_user else color_red(username)

    # Display the formatted message
    # print(f"{colored_username}: {formatted_message}")
    return formatted_message


def parse_bold(message):
    """
    Parses **bold** text with increased intensity.
    """
    return re.sub(r'\*\*(.*?)\*\*', lambda m: f'\033[2m{m.group(1)}\033[0m', message)

def parse_italics(message):
    """
    Parses _italics_ text.
    """
    return re.sub(r'\_(.*?)\_', lambda m: f'\033[3m{m.group(1)}\033[0m', message)

import re

def parse_italics(message):
    """
    Parses /italic/ text.
    """
    return re.sub(r'/(.*?)/', lambda m: f'\033[3m{m.group(1)}\033[0m', message)

def color_blue(text):
    """
    Colors the given text in blue.
    """
    return f'\033[94m{text}\033[0m'  # Blue text


def display_hyperlinks(message):
    """
    Finds and colors hyperlinks within a message in blue.
    """

    def replace_with_blue_link(match):
        return color_blue(match.group(0))

    # Replace all hyperlinks with blue-colored versions
    message_with_blue_links = re.sub(r'(http[s]?://[^\s]+)', replace_with_blue_link, message)

    return message_with_blue_links


def color_green(text):
    return f'\033[92m{text}\033[0m'  # Green text

def color_red(text):
    return f'\033[91m{text}\033[0m'  # Red text