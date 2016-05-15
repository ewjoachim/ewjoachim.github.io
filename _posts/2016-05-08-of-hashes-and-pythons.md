# Of Hashes and Pythons

I posted the following code on a [tweet](https://twitter.com/Ewjoachim/status/728610568886718466) today
and subsequently had a very interesting talk answering [questions](https://twitter.com/codingrixx/status/728616489318789120) about this, which I'll sumarize here. There might also be new material, too.

{% capture content %}{% highlight python %}
class A(object):
    def __hash__(self):
        return id(self)
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=1 content=content type='input' %}

{% capture content %}{% highlight python %}
class B(object):
    def __hash__(self):
        return 1
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=2 content=content type='input' %}

{% capture content %}{% highlight python %}
%%timeit
{A() for a in range(10000)}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=3 content=content type='input' %}
<pre>
100 loops, best of 3: 4.63 ms per loop
</pre>

{% capture content %}{% highlight python %}
%%timeit
{B() for a in range(10000)}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=4 content=content type='input' %}
<pre>
1 loop, best of 3: 1.42 s per loop
</pre>

## So what's happening here ?

Here's a textual version of the code above.

First I create a class `A` whose ``__hash__`` method returns the result of `id(self)` which mean more or less "the value of a pointer on `self`.

Then I create a class `B` whose ``__hash__`` method returns something quite simpler : the constant 1.

Putting ten thousand instances of `A` in a set takes 4 ms, putting 10 thousand instances of `B` should *logically* take less, because the hash is easier to compute and you don't have to store ten thousand different hashes, right ? Nope. It take longer. 317 times longer.

**Note:** The hash of an object is just an integer with the following property : if 2 objects are equal, then their hashes are equal too. (The opposite is not always true, see the remarks at the end of the post)

**Note 2:** In this post, I'm talking a lot about sets. I could say exactly the same thing about dicts. Sets are easier to manipulate in this example.

## What happens when I put something in a set ?

Let's play a bit. Introducing Verbose, a class that talks all the time.

Instances have a name, and we do 2 things:

 1. If 2 instances share the same name, we say they're equal, through `__eq__` (and talk a bit).
 2. Through `__hash__`, we set the hash of instances to be solely based on their name (and talk a bit).

{% capture content %}{% highlight python %}
class Verbose(object):
    
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        """
        __eq__(for "equal") is used to determine
        the result of:
        Verbose() == other
        """
        equal = self.name == other.name
        print("Is {} equal to {} ? {}.".format(self, other, equal))
        return equal
    
    def __hash__(self):
        """
        Hashable objects need to implement __hash__,
        that should return integers, with this
        property: 2 equal objects should return
        the same hash.
        """
        hash_value = hash(self.name)
        print("Asking the hash for {} which is {}.".format(self, hash_value))
        return hash_value
        
    def __repr__(self):
        """
        This is just so that our prints looks clean
        """
        return self.name
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=5 content=content type='input' %}

Play time !

{% capture content %}{% highlight python %}
Verbose("a") == Verbose("b")
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=6 content=content type='input' %}
<pre>
Is a equal to b ? False.
</pre>
{% capture content %}{% highlight python %}
False
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=6 content=content type='output' %}

{% capture content %}{% highlight python %}
{Verbose("a")}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=7 content=content type='input' %}
<pre>
Asking the hash for a which is -1212919011480583274.
</pre>
{% capture content %}{% highlight python %}
{a}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=7 content=content type='output' %}

{% capture content %}{% highlight python %}
{Verbose("a"), Verbose("b")}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=8 content=content type='input' %}
<pre>
Asking the hash for b which is 5265123888727380584.
Asking the hash for a which is -1212919011480583274.
</pre>
{% capture content %}{% highlight python %}
{b, a}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=8 content=content type='output' %}

{% capture content %}{% highlight python %}
{Verbose("a"), Verbose("a")}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=9 content=content type='input' %}
<pre>
Asking the hash for a which is -1212919011480583274.
Asking the hash for a which is -1212919011480583274.
Is a equal to a ? True.
</pre>
{% capture content %}{% highlight python %}
{a}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=9 content=content type='output' %}

When I put an object in a set, these things happen :

 1. We compute the hash of the object
 2. We see if the hash is already in our set
 3. If so, we get the objects that share the same hash, they're potential matches
 4. We wheck if our object is equal to any of that list.
 5. If so, it's already in our set, so no need to add it again.
 
What would happen if 2 objects had the same hash, but were not equal ?

{% capture content %}{% highlight python %}
class Verbose2(Verbose):
    def __hash__(self):
        return 1
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=10 content=content type='input' %}

{% capture content %}{% highlight python %}
{Verbose2("a"), Verbose2("b"), Verbose2("c"), Verbose2("d"), Verbose2("e"), Verbose2("f")}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=11 content=content type='input' %}
<pre>
Is f equal to e ? False.
Is f equal to d ? False.
Is e equal to d ? False.
Is f equal to c ? False.
Is e equal to c ? False.
Is d equal to c ? False.
Is f equal to b ? False.
Is e equal to b ? False.
Is d equal to b ? False.
Is c equal to b ? False.
Is f equal to a ? False.
Is e equal to a ? False.
Is d equal to a ? False.
Is c equal to a ? False.
Is b equal to a ? False.
</pre>
{% capture content %}{% highlight python %}
{f, a, c, b, e, d}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=11 content=content type='output' %}

Thats 15 comparisons for 6 objects. Each object gets compared to all the others. The number of comparison is `6 * 5 / 2`

{% capture content %}{% highlight python %}
n = 6
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=12 content=content type='input' %}

{% capture content %}{% highlight python %}
def number_of_comparisons(n):
    return n * (n - 1) // 2

number_of_comparisons(6)
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=13 content=content type='input' %}
{% capture content %}{% highlight python %}
15
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=13 content=content type='output' %}

So this is what is happening for our initial bad example : there are 10 000 objects that all get compared to each other.

{% capture content %}{% highlight python %}
number_of_comparisons(10000)
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=14 content=content type='input' %}
{% capture content %}{% highlight python %}
49995000
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=14 content=content type='output' %}

That's ~50 millions.

## At this point, you might ask :

*"But you said elusively in your earliest list that 'We see if the hash is already in our set'. Isn't it the same problem ? We have to check all the values !*"

And yes, if a hash could be anything, that would be true. Fortunately, we know something about hashes : they're integers. A comparison between any objects can give 2 results : equal or not equal. A comparison between integers can give 3 results : less, equal, greater.

What happens behind the scene may depend on the python implemention. Better than telling you things that Python does that we cannot **test** here, let's give an example of what à Python implementation **might** do.

Python could place all our values in a [Binary Tree](https://en.wikipedia.org/wiki/Binary_tree) (`btree`). A binary tree is a way to organize sortable elements that look a lot like the game where you have to guess someone's number when they only tell you plus or minus. This allows for very efficient fetching of your data (`log2(n)`)

## So that's it, then

Now we know why the `A` class is fast and the `B` class is so very very slow.

Thank you very much. The show's finished. What you want more ? Ok, let's get you more !

## What happens when the hash is not really reliable ?

{% capture content %}{% highlight python %}
import random
class C(object):
    def __hash__(self):
        return random.randint(0, 10)
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=15 content=content type='input' %}

{% capture content %}{% highlight python %}
c = C()
s = {c}
print ("Is c in the set of s that contains only c ?", c in s)
print ("And what if I ask you 20 times the question ?", any(c in s for i in range(20)))
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=16 content=content type='input' %}
<pre>
Is c in the set of s that contains only c ? False
And what if I ask you 20 times the question ? True
</pre>

## Why do they say mutable objects should not be hashable ?

(Mutable objects mean objects that you can modify after they've been created). Hashes are computed only when the object is first put in a set.

{% capture content %}{% highlight python %}
a = Verbose("a")
s = {a}
a.name = "b"
s.add(Verbose("b"))
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=17 content=content type='input' %}
<pre>
Asking the hash for a which is -1212919011480583274.
Asking the hash for b which is 5265123888727380584.
</pre>

{% capture content %}{% highlight python %}
s
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=18 content=content type='input' %}
{% capture content %}{% highlight python %}
{b, b}
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=18 content=content type='output' %}

We've mutated our object `a` to a `b` after we put it in a set, and now the set contains 2 equal `b` objects. We've broken our set ! So that's why `list`s and `dict`s (which are mutables) cannot be put in sets, but `tuple`s and `frozenset`s (which are immutable) can. 

## Do we really need hash AND eq to compare objects ? isn't hash alone enough ?

Given that there's a lower and upper limit to the hashes integer values, there are not lots of possible hashes compared to the number of different objects that might exist, so there are not enough integers to give a unique one to all the possible objects in universe. Here are a few examples :

{% capture content %}{% highlight python %}
hash(1.000000000000001) == hash(2561)
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=19 content=content type='input' %}
{% capture content %}{% highlight python %}
True
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=19 content=content type='output' %}

{% capture content %}{% highlight python %}
hash(object) == hash(hash(object))
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=20 content=content type='input' %}
{% capture content %}{% highlight python %}
True
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count=20 content=content type='output' %}

So, would you use Python if you knew that **sometimes**, you get a random object disappearing from a set or a dict just because it has the same hash as an existing object ? You'd probably run away, and I'd do too. But it's ok, Python has our back. \o/

## [Update : ] Is this a security issue ?

Well it can be. I didn't knew about this until [@_rami_](https://twitter.com/_rami_) showed me, but, yes, this can be
quite a security issue because if it can help an attacker to bring your server on its knees. See [the video](https://media.ccc.de/v/28c3-4680-en-effective_dos_attacks_against_web_application_platforms) and [the discussion](https://twitter.com/_rami_/status/728880347111362560) on the subject.


## Conclusion

That's all, folks. Thanks a lot to [@rixx](https://twitter.com/codingrixx) for the inspiration of writing this as a blog post.

I'm all ears for suggestions and improvements regarding both the content and the format of this. I might do it again later.

See ya !

*Joachim Jablon*

(Creative Commons : BY-NC)

