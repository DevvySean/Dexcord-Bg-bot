import discord
from discord.ext import commands
from pydexcom import Dexcom
import asyncio
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from requests.exceptions import JSONDecodeError
from bot.data_fetcher import get_readings_from_db
from bot.openai_analyzer import analyze_blood_sugar_trends
from bot.models import BloodSugar, engine 

load_dotenv()

Session = sessionmaker(bind=engine)
session = Session()


intents = discord.Intents.all()
intents.typing = True
intents.presences = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.loop.create_task(bloodAlert())


@bot.event
async def on_message(message):
    if message.author != bot.user:
        await bot.process_commands(message)

        
async def bloodAlert():
    timer = 600
    channel = bot.get_channel(1158039959727505428)
    while True:
        
        try:
            
            dexcom = Dexcom(os.getenv('DEXCOM_USERNAME'), os.getenv('DEXCOM_PASSWORD'), ous=True) # ous=True if outside of US
            glucose_reading = dexcom.get_current_glucose_reading().mmol_l
            bloodArrowDirection = dexcom.get_current_glucose_reading().trend_arrow
            bloodDescription = dexcom.get_current_glucose_reading().trend_description
            

            # If bloods are less than or equal to 6 and falling slightly, falling or falling rapidly we will alert
            if glucose_reading <= 6 and bloodDescription in ['falling slightly', 'falling', 'falling rapidly']:
                
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**Warning Bloods Are** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")
            
            # If bloods are less than or equal to 6 and steady, rising slightly, rising or rising rapidly we will alert
            elif glucose_reading <= 6 and bloodDescription in ['steady', 'rising slightly', 'rising', 'rising rapidly']:
                
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**Warning Bloods Are** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")

            # If bloods are less than or equal to 5 and falling slightly, falling or falling rapidly we will alert
            elif glucose_reading <= 5 and bloodDescription in ['falling slightly', 'falling', 'falling rapidly']:
                
                timer = 300
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**EMERGENCY!! LOW BLOODS** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")
            
            # If bloods are greater than or equal to 16 and falling slightly, falling or falling rapidly we will alert
            elif glucose_reading >= 16 and bloodDescription in ['rising slightly', 'rising', 'rising rapidly']:
                
                
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**Warning Bloods Are Greater Than 16 & Rising** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")
            
            elif glucose_reading >= 16 and bloodDescription in ['falling slightly', 'falling', 'falling rapidly', 'steady']:
                
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**Warning Bloods Are** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")

            # If bloods are greater than or equal to 20 and rising slightly, rising or rising rapidly we will alert
            elif glucose_reading >= 20 and bloodDescription in ['rising slightly', 'rising', 'rising rapidly']:
                
                timer = 300
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**EMERGENCY!! HIGH BLOODS** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")

            elif glucose_reading >= 20 and bloodDescription in ['falling slightly', 'falling', 'falling rapidly', 'steady']:
                
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**Warning Bloods Are** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription + "<@228673848118083584> <@500791793541971980>")
                
            else:
                
                new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
                session.add(new_reading)
                session.commit()
                await channel.send(f"**NORMAL BLOODS** - {glucose_reading}" + " " + bloodArrowDirection + " " + bloodDescription)
                
            await asyncio.sleep(timer)

        except AttributeError as e:
             await channel.send(f"Error - Unable to get bg data! {str(e)} <@228673848118083584> <@500791793541971980>")
             await asyncio.sleep(600)

        except JSONDecodeError as e:
            await channel.send(f"Error - JSONDecodeError! {str(e)} <@228673848118083584> <@500791793541971980>")
            await asyncio.sleep(600)


@bot.command(name='trends')
async def trends(ctx, time_range='24h'):

    readings = get_readings_from_db(session, time_range)

    if not readings:
        await ctx.send(f"No blood sugar readings found for the last {time_range}.")
        return

    # Analyze the trends using OpenAI
    trends_analysis = analyze_blood_sugar_trends(readings, time_range)

    # Send the analysis to the Discord channel
    await ctx.send(f"**Blood Sugar Trends for the last {time_range}:**\n{trends_analysis}")



@bot.command()
async def bg(ctx):

    dexcom = Dexcom(os.getenv('DEXCOM_USERNAME'), os.getenv('DEXCOM_PASSWORD'), ous=True) # ous=True if outside of US
    glucose_reading = dexcom.get_current_glucose_reading().mmol_l
    bloodArrowDirection = dexcom.get_current_glucose_reading().trend_arrow
    bloodDescription = dexcom.get_current_glucose_reading().trend_description
    

    if glucose_reading <= 5:

        await ctx.send(str(glucose_reading) +  " " + bloodArrowDirection + ". They are currently " + bloodDescription)
        new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
        session.add(new_reading)
        session.commit()
    
    elif glucose_reading >= 5.1 and glucose_reading < 10:

        await ctx.send(str(glucose_reading) +  " " + bloodArrowDirection + ". They are currently " + bloodDescription)
        new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
        session.add(new_reading)
        session.commit()

    else:

        await ctx.send(str(glucose_reading) +  " " + bloodArrowDirection + ". They are currently " + bloodDescription)
        new_reading = BloodSugar(blood_glucose_value=glucose_reading, blood_description=bloodDescription, timestamp=datetime.now())
        session.add(new_reading)
        session.commit()

        

bot.run(os.getenv('DISCORD_TOKEN'))

