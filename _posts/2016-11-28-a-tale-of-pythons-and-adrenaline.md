---
title: A tale of Python and Adrenaline
icon: heartbeat
---

The full story behind the talk I gave tonight at the Paris Python Meetup on Python 3.6

{{ excerpt_separator }}

So first, if you want the slides, they're in French, I'll translate on demande (please,
really, fell free !) or if I make this talk in an international context.

You can have them here : [Ladies and Gentlemen, the Amazing Python 3.6 !](/assets/Python 3.6.slides.html)

The original Jupyter notebook with the original typos is available here :
[Jupyter Notebook](https://gist.github.com/ewjoachim/8fb6352be242fae40aba471664dcbaf8)

## Disclamer

This is an only sightly romanticized version of the facts as they happened.

## So what happened ?

First the context : I was supposed to give this talk tomorrow. I wrote it yesterday and planned to spend
a few more hours on it tonight. At 5PM, [the Meetup](https://www.meetup.com/fr-FR/Paris-py-Python-Django-friends/)
fantastic organizers annonced that one of the planned speakers was unavailable. Given I was to give this talk
(in another meetup) on the following day, I volonteered.

Another bit of context : I recently got my hands on (or more precisely got one hand encircled by) a connected watch.

Another bit of context : I'm a [Jupyter](http://jupyter.org/) fanboy. We that part you already know if you've been
following this blog.

Lastly: When adrenaline flows in my brain, I become convinced I can do anything.

## So... What happened !?

Well I realized it would have been a nice opportunity to try using my watch as a slides remote control. But that
would have needed planning in advance, developing, reserching etc.

"Heck, I'm using Python. My brain is flowing adrenaline I can do anything. So let's go.", did I think.
At 6.45 PM, 15 minutes before the meetup would start, my brain did.

I was using Jupyter for my presentation, which meant my slides would be exported directly as HTML slides
using Reveal.js. The export command was :

```console
$ jupyter nbconvert Python\ 3.6.ipynb --to slides --post serve
```

(I originally added `--reveal-prefix reveal.js` with a locally downloaded reveal.js to make sure
it would work even without Internet access but that proved useless, as the internet from my phone
was enough)

Then a quick skim at the [Reveal.js](https://github.com/hakimel/reveal.js/) README told me that a javascript
call to `Reveal.next()` would trigger the next slide.

Then I rememberd about [IFTTT](https://ifttt.com/) and their [Do button](https://ifttt.com/do_button) was
compatible with my watch. So I knew I could have my watch trigger an API call on a public server.

At that point, the first talk started, about "Creating your [Flask](http://flask.pocoo.org/)
API in 5 minutes". I remebered that I had once deployed a small flask website using
[Python Anywhere](https://www.pythonanywhere.com/) which definitely lived up to its name.

I cloned the project I had done an quicky [repurposed it](https://github.com/ewjoachim/bttn_flask/commits/master)
for its new goal : have 2 API : one that would set a flag ("Go to next slide") and one that would read and
reset it. It took 3 commits to works, including one aptly named ["haaaaaands"](https://xkcd.com/1296/) but then
it worked. It's obviously bad code, but time was of the essence here.

Here's the code, BTW:

```python
from flask import Flask, Response
from flask_sslify import SSLify


app = Flask(__name__)

SSLify(app)

file = "bla.txt"


def empty():
    with open(file, "w"):
        pass

empty()


@app.route("/get")
def get():
    with open(file, "r") as f:
        c = f.read()
    empty()
    resp = Response(c)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/set")
def set():
    with open(file, "w") as f:
        f.write("true")

    resp = Response("true")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

```

I then created an IFTTT "do button > Maker" reciepe that would call my "set" api when I'd tap on my watch.
I would have shared the reciepe with you but [meh](https://www.reddit.com/r/ifttt/comments/5elxhz/how_do_i_make_my_applet_public/).
But then it's not really hard to do.


Lastly wrote a small bit of javascript that would poll every 800ms and call `Reveal.next()` whenever the
polled result was "true". Yes I know that in 2016, websockets are a thing, and I'm a man of the past but hey.


```html
<script>
a = function(){$.get("https://ewjoachim.pythonanywhere.com/get", function(data){if (data == "true"){Reveal.next()}})};
setInterval(a, 800);
</script>
```

Of course it failed because at first I didn't think about those pesky `Access-Control-Allow-Origin` but
once that was take care of, it worked. With a 10 second delay, but i worked nethertheless.

And then it was my turn to go on stage.

And it worked on stage.

And I delivered my talk, feeling filled with so much energy I could have zapped the light bulbs with
my confidence.

## Conclusion

Tinker away. Do things. Make stuff. Useless stuff. The useless stuff of today will be a brick in the new stuff
you do tomorrow and all in all, you'll end up happier. Be happy. Contribute to Open source software. Be happier.
Don't listen to the advice of random folks on the Internet telling you how to live your life.


Yours, truly,

Joachim
