import re
from colorama import Fore, Style  # Assuming you are using the colorama library for colors

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
    colored_username = color_red(username) if is_current_user else color_green(username)

    # Display the formatted message
    return f"{colored_username}:{color_green(formatted_message)}"

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

def display_hyperlinks(message):
    """
    Finds and colors hyperlinks within a message in blue.
    """

    def replace_with_blue_link(match):
        return color_blue(match.group(0))

    # Replace all hyperlinks with blue-colored versions
    message_with_blue_links = re.sub(r'(http[s]?://[^\s]+)', replace_with_blue_link, message)

    return message_with_blue_links

def color_blue(text):
    """
    Colors the given text in blue.
    """
    return f'{Fore.BLUE}{text}{Style.RESET_ALL}'

def color_green(text):
    """
    Colors the given text in green.
    """
    return f'{Fore.GREEN}{text}{Style.RESET_ALL}'

def color_red(text):
    """
    Colors the given text in red.
    """
    return f'{Fore.RED}{text}{Style.RESET_ALL}'

# Example usage
username = "User123"
message = "This is a **bold** and _italic_ message with a link: https://example.com"
is_current_user = True
formatted_message = display_message(username, message, is_current_user)
print(formatted_message)
