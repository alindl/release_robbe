# Release Robbe
Get and manage new songs and artists from Spotify

## What's it gonna do?
Let's go through the workflow of the thing:

- Either get new songs of artists from some source or top 10 songs from a Greylist

- Get the artists for new releases
    - You can get them through playlists, a local Allowlist or the artists you follow
        - You select which playlists you want to scan for artists.
- The programm goes through the list of artists.
- You have an Allowlist, Greylist and Blocklist.
    - The Allowlist is made up of all artists you are certain of, are fine to you
    - The Blocklist contains artists you don't want to get new stuff from (Gangnam Style was fun, but are you really that much into PSY?)
    - Finally the Greylist artists are new to you, so maybe you want to check out their stuff at a later time.
- It's going to ask you where to put new additions 
    - It sucks on the first run, because there is no data on the lists.
    - New artists go on the Greylist anyhow.
    - You choose one of the following:
        - Add new songs, don't put on the Allowlist
        - Add new songs AND put on the Allowlist
        - Ignore new songs, but don't put the artist on the Blocklist
        - Ignore new songs AND put them on the Blocklist
        - All of the 4 above again, but this time for ALL artists
        - If the artist is on the Greylist, it's going to be ignored. You can get top songs as mentioned above
    - It's going to ignore artists from the Blocklist and won't ask you if they are on the Grey or Allowlist.
- Going through the artists, it's going to save all songs that have been released since a date you specified. 
    - Or top songs for entries on the Greylist if you said so
    - While it tries to remove live versions and duplicates, it's not perfect though.
- After it has saved a number of songs, you can choose a playlist on Spotify to add them to.


## Prerequisites
### Side note:
You gotta make a Spotify app. I know it's annoying, but here's why:
- This are the scopes we need:
    - playlist-read-collaborative
        - So it can get the artists on your collab lists
    - playlist-read-private
        - Maybe you even want to get artists from a private list
    - playlist-modify-private
        - This is to add the new tracks to a private playlist, if you choose to
    - playlist-modify-public
        - You get the gist, don't you?
    - user-follow-read
        - You can also use the list of artists you follow as a source
- Nobody is going to see your data, except for you and the NSA of course.
    - Please check out my yucky code, there's no hidden server this data is sent to.
        - Really do, because I feel like my code isn't very efficient, especially on memory usage.
    - The only persistent data is going to be your lists, which are saved locally
        - If there's Spice Girls on there and you don't want anybody to know, encrypt and lock your drives, I can't change that 😉

### Make a Spotify app:
Let's make it short and simple:
- Go here: https://developer.spotify.com/dashboard/
- Log in
- Create an app
    - Call it whatever you want. Bonus points for creativity, but I don't get to see the name anyway.
- Save/Memorize/Tattoo your Client ID and Client Secret
- Run my code, put those things in there, as well as your username
- Those details are going to stay in a local configuration file
- Done, here's a cookie for your effort 🍪

#TODO
- Track duplication detection: Same name && length -> duplicate
    - Worth the effort? Needs more data at duplicate detection 
        - More data, slower time complexity because of data structure
- Window sizes
