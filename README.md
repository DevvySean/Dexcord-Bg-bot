# Dexcord Bot

This bot uses pydexcom pypi package - https://pypi.org/project/pydexcom/ to get the users blood sugar readings from their API,  it writes the readings to a database and integrates with discord python library to send blood sugar alerts into the chosen channel. 

You can adjust timers to set the frequency of the alerts etc. 

Also there is a command for !trends and !trends week which will grab data from the database and pass it to openai to provide insights and analysis.

