# JetBridge Test
So... my laptop was broken, and here is my piece of art made in one night.  

## Basis
This is a social network where people can post 4 photos, using different templates and invite other users to this network.  
Users can see how many users have joined the network, and how many of them have been invited by a particular user.

On the main page you will alway see last 10 joined users. You can view their profiles. Also you can view and edit your profile.

## Authentification
In this app you can Login, Logout and Sign Up with or without invitation code

### A few words about invites
Code is a model in db linked with User. It forms using integer and its own type.

The integer will be encoded to base58 using BitCoin Alphabet, and the type is 'P' for personal, 'E' for enterprise, 'H' for host. 
Also invitation link storing this and qr code storing this link will be generated.
Using this link will automaticly fill up 'Invitation code' field on registration page.

## Generator
You can also generate some random users using django shell.  
To do this:
```python
from generator.generator import Generator
g = Generator()
g.generate()
```
It's working slow cause it have several 5 request for each user with 0.7 seconds timeout after each request, and also image cropping takes some time.
But if set `periods` in config to 3 it will take about 5 mins I think.

> I don't know wath else to write. Due to laptop breakdown my terms have shifted, so this code gets a little messy, sowwy)
