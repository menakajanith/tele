import asyncio
import re
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

GROUP_ID = '-1002368771992'  # Replace with your actual group ID

# Function to calculate the age from the given date of birth (DD/MM/YYYY)
def calculate_age(dob):
    try:
        dob_day, dob_month, dob_year = map(int, dob.split('/'))
        today = datetime.today()
        age = today.year - dob_year - ((today.month, today.day) < (dob_month, dob_day))
        return age
    except ValueError:
        return None

async def start(update: Update, context) -> None:
    # Only process the command if it's in a private chat
    if update.message.chat.type == "private":
        user_name = update.effective_user.first_name
        message = f"Hi, {user_name}❤️\nHow can I help you today?"

        # Creating regular (non-inline) buttons in one row (horizontally aligned)
        keyboard = [
            [KeyboardButton("About"), KeyboardButton("Request")]
        ]

        # Adding the keyboard as a reply markup
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        # Sending message with keyboard
        await update.message.reply_text(message, reply_markup=reply_markup)

# Function to handle button press
async def handle_button(update: Update, context) -> None:
    # Only process the button actions if it's in a private chat
    if update.message.chat.type == "private":
        if update.message.text == "About":
            image_path = "lo.jpg"  # Replace with actual local image path

            with open(image_path, 'rb') as image_file:
                await update.message.reply_photo(
                    photo=InputFile(image_file),
                    caption=( 
                        "මම වැඩ කරන්නේ ALPHA ROG එකේ. මම කැමතියි අනික් අයට උදව් කරන්න 🤝, "
                        "පොත් කියවන්න 📚, ෆිල්ම්ස් බලන්න 🎞 වගේ ඒවට. "
                        "මට සිංදු 🎵 කියන්නත් පුලුවන්.. "
                        "හරි හරි ඉතිම් පොඩ්ඩක් අහන් ඉන්න අමාරු ඇති..😋\n\n"
                        f"තෑන්ක් යූ {update.effective_user.first_name}. ❤️\n\n"
                        "ඉතිම් මාව බලන්න ආවට..❤️"
                    )
                )
        elif update.message.text == "Request":
            message = await update.message.reply_text(
                "ඔබට දැන ගැනීමට කැමති මිත්‍යාව පිළිබදව අපිට කියන්න...\n\n"
                "ඔබ මිත්‍යා රචකයෙකු වීමට අවැසි කෙනෙක් නම් ⏳... ",
                reply_markup=ReplyKeyboardRemove()  # Remove the keyboard
            )
            context.user_data['request_step'] = 'name'
            await asyncio.sleep(5)  # Wait for 5 seconds
            await message.delete()
            await update.message.reply_text("ඔබගේ නම ලබා දෙන්න.")

        elif context.user_data.get('request_step') == 'name':
            user_name = update.message.text
            telegram_username = update.effective_user.username  # Get the Telegram username

            # Validate that the name contains only Sinhala, English letters, and spaces
            if not re.match(r"^[\u0D80-\u0DFFA-Za-z\s]+$", user_name):
                await update.message.reply_text("කරුණාකර නමට පමණක් අකුරු සහ ස්පේස් ලබා දෙන්න. (අංක සහ විශේෂ දේවල් ඇඩ් කිරිමේන වලකින්න)")

                return  # Skip the next steps if the name is invalid

            # Check if the entered name matches the Telegram username (case insensitive)
            if telegram_username and user_name.lower() != telegram_username.lower():
                await update.message.reply_text(f"ඔබගේ නම {user_name} සහ Telegram නාමය @{telegram_username} නොගැලපේ. කරුණාකර නිවැරදි නමක් ලබා දෙන්න.")
                return  # Stop if the names don't match

            context.user_data['name'] = user_name
            await update.message.reply_text(f"ඔයාගේ නම {user_name} වෙයි. දැන්, ඔබගේ වයස පවසන්න.")
            context.user_data['request_step'] = 'age'

        elif context.user_data.get('request_step') == 'age':
            user_age = update.message.text

            # Ensure age is a number and within a valid range (10-80)
            if not user_age.isdigit():
                await update.message.reply_text("කරුණාකර ඔබගේ වයස අංකයක් ලෙසම ලබා දෙන්න. (උදා: 25)")
                return
            elif int(user_age) < 10 or int(user_age) > 80:
                await update.message.reply_text("කරුණාකර ඔබගේ වයස නිවැරදිව ලබා දෙන්න. (අවම වයස 10 සහ උපරිම වයස 80 වේ)")
                return

            context.user_data['age'] = user_age
            await update.message.reply_text(f"ඔයාගේ වයස {user_age} වෙයි. දැන්, ඔබගේ උපන් දිනය ලබා දෙන්න (DD/MM/YYYY).")
            context.user_data['request_step'] = 'dob'

        elif context.user_data.get('request_step') == 'dob':
            dob = update.message.text

            # Validate the date format and handle errors
            dob_age = calculate_age(dob)

            if dob_age is None:
                await update.message.reply_text("කරුණාකර ඔබගේ උපන් දිනය DD/MM/YYYY ලෙසම ලබා දෙන්න. (උදා: 25/12/2000)")
                return

            # Check if the calculated age matches the age entered earlier
            if dob_age != int(context.user_data['age']):
                await update.message.reply_text(
                    f"ඔබගේ වයස {context.user_data['age']} වසර වන අතර, ඔබගේ උපන් දිනයට අනුව වයස {dob_age} වේ. "
                    "කරුණාකර නිවැරදි උපන් දිනය ලබා දෙන්න."
                )
                return

            context.user_data['dob'] = dob
            await update.message.reply_text(f"ඔබගේ උපන් දිනය: {dob}\nඔබගේ කතාව ලබා දෙන්න.")
            context.user_data['request_step'] = 'story'

        elif context.user_data.get('request_step') == 'story':
            story = update.message.text  # Capture the story the user writes
            context.user_data['story'] = story

            # Send the user's profile picture first (only in private chat)
            user = update.effective_user
            photos = await user.get_profile_photos()

            # Check if the user has a profile photo
            if photos.total_count > 0:
                photo = photos.photos[0][-1]  # Get the highest resolution image
            else:
                # Default image if no profile photo exists
                photo = "lo2.jpg"  # Replace with your default image path

            # Create a caption with the user's details and story
            caption = (
                f"ඔබගේ නම: {context.user_data['name']}\n"
                f"ඔබගේ වයස: {context.user_data['age']}\n"
                f"ඔබගේ උපන් දිනය: {context.user_data['dob']}\n"
                f"ඔබ ලියූ කතාවක්: {story}"
            )
            
            # Create a reply_markup with the "Send Now" button (for private chat)
            keyboard = [
                [InlineKeyboardButton("Send Now", callback_data="send_now")]
            ]
            
            # Send profile photo with the final details and the inline button in private chat
            await update.message.reply_photo(
                photo=photo, 
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)  # Add inline button
            )

# Callback function to handle the inline button click
async def handle_callback(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    
    if query.data == "send_now":
        # Retrieve user data from context
        user_name = context.user_data['name']
        user_age = context.user_data['age']
        user_dob = context.user_data['dob']
        user_story = context.user_data['story']
        
        # Create caption with user details
        caption = (
            f"ඔබගේ නම: {user_name}\n"
            f"ඔබගේ වයස: {user_age}\n"
            f"ඔබගේ උපන් දිනය: {user_dob}\n"
            f"ඔබ ලියූ කතාවක්: {user_story}"
        )
        
        # Get user's profile photo
        user = update.effective_user
        photos = await user.get_profile_photos()
        
        if photos.total_count > 0:
            photo = photos.photos[0][-1]  # Get the highest resolution image
        else:
            # Default image if no profile photo exists
            photo = "lo2.jpg"  # Replace with your default image path
            
        # Send the photo and details to the group
        await context.bot.send_photo(
            chat_id=GROUP_ID,  # Your group ID
            photo=photo,
            caption=caption
        )
        
        # Inform the user in the private chat
        await query.message.reply_text("ඔබගේ තොරතුරු සාර්ථකව යවා ඇත.",
                                       reply_markup=ReplyKeyboardMarkup([ 
                                           [KeyboardButton("About"), KeyboardButton("Request")] 
                                       ], resize_keyboard=True))
        # Clear user data after completion
        context.user_data.clear()

# Set up the application
def main():
    application = Application.builder().token("7611728916:AAGryNP6Uhhea7ar6_hxVFvTf8PYraCDAVU").build()  # Replace with your bot's API key

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
