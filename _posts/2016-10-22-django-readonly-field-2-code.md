---
title: Django Readonly Field - Chapter 2 - The code
icon: code
date: 2016-10-22 00:10:00
---

This article is part of a series on [Django Readonly Field]({% post_url 2016-10-22-django-readonly-field-1-lib %}). Here, we see **how it works**.

{{ excerpt_separator }}

## Exploring the project

First, you can see that the [GitHub project](https://github.com/novafloss/django-readonly-field) contains quite a few files, but the really interesting part for today is the [`django_readonly_field` subdirectory](https://github.com/novafloss/django-readonly-field/tree/b8c3878976/django_readonly_field). So that's only 3 files and [59 lines of code](https://codecov.io/gh/novafloss/django-readonly-field/list/b8c38789769e44779574bdbc508fc0358d9e1464) according to my coverage data.

Let's look at those files.

## `__init__.py`, the entry point

{% capture content %}{% highlight python %}
__version__ = '1.0.1'

default_app_config = "django_readonly_field.apps.Readonly"
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

You can see that there's not much done here. The version is useful to have here for the lib to easily introspect its own version if need be. The `default_app_config` is interesting. According to the [Django documentation](https://docs.djangoproject.com/en/1.10/ref/applications/#configuring-applications), this variable will be used if the module it's in is placed in the list of `INSTALLED_APPS`. So now we kind of have a idea how the app is to be used.

The value seems to be a class defined in `apps.py`. Let's go and check that.

## `apps.py`, switching the compiler

{% capture content %}{% highlight python %}
from __future__ import unicode_literals

from django.apps import AppConfig


class Readonly(AppConfig):
    name = 'django_readonly_field'

    def ready(self):
        from django.db import connection
        from django.db import utils

        readonly_compiler_module = "django_readonly_field.compiler"

        # Change the current value (this is mostly important for the tests)
        connection.ops.compiler_module = readonly_compiler_module

        original_load_backend = utils.load_backend

        def custom_load_backend(*args, **kwargs):
            backend = original_load_backend(*args, **kwargs)

            class ReadOnlyBackend(object):
                @staticmethod
                def DatabaseWrapper(*args2, **kwargs2):
                    connection = backend.DatabaseWrapper(*args2, **kwargs2)
                    connection.ops.compiler_module = readonly_compiler_module
                    return connection

            return ReadOnlyBackend

        # Make sure all future values will be changed too
        # (this is mostly important for the real life)
        utils.load_backend = custom_load_backend

{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

Let's dive in !

{% capture content %}{% highlight python %}
class Readonly(AppConfig):
    name = 'django_readonly_field'

    def ready(self):
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

From the Django documentation above, we learn that the `AppConfig.ready` method is called as part of `django.start()` which is called at the very beginning of a django process.

{% capture content %}{% highlight python %}
from django.db import connection

readonly_compiler_module = "django_readonly_field.compiler"

# Change the current value (this is mostly important for the tests)
connection.ops.compiler_module = readonly_compiler_module

{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

So the main step here is that we replace the string in [`django.db.connection.ops.compile_module`](https://github.com/django/django/blob/8119b67/django/db/backends/base/operations.py#L21) with `'django_readonly_field'`.

This string is used [here](https://github.com/django/django/blob/8119b67/django/db/backends/base/operations.py#L304-L312).

{% capture content %}{% highlight python %}
# django/django/db/backends/base/operations.py in BaseDatabaseOperations
def compiler(self, compiler_name):
    """
    Returns the SQLCompiler class corresponding to the given name,
    in the namespace corresponding to the `compiler_module` attribute
    on this backend.
    """
    if self._cache is None:
        self._cache = import_module(self.compiler_module)
    return getattr(self._cache, compiler_name)
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

It is the main link between the `DatabaseWrapper` object which represent a connection between Django and its Database, and the SQLCompiler class which is how django transforms methods calls into SQL.

The idea is that we'll use our very own compiler that will remove the fields marked as readonly from write queries.

### The thread problem

One thing that was hard to foresee is that the object we're modifying here (actually, the whole `DatabaseWrapper`) is completely recreated in every thread (it's local to the thread), and Django will use a new thread for every connection. This means that the object we're modifying here will be thrown away shortly, except in the tests that are mono-threaded.

Consequently, we need to make the same modification in every new version of the `DatabaseWrapper`. We'll do this by modifying the `load_backend` function that is defined [here](https://github.com/django/django/blob/9f4e031/django/db/utils.py#L105) and used [here](https://github.com/django/django/blob/9b9c8c4/django/db/utils.py#L204-L214). The main advantage of modifying this function in particular is that it's not thread local (there will be only one instance of this function, whatever the number of threads used) but all the threads will use this function.

The next question is how do we make `load_backend` return a patched `DatabaseWrapper`?

{% capture content %}{% highlight python %}
 original_load_backend = utils.load_backend

def custom_load_backend(*args, **kwargs):
    backend = original_load_backend(*args, **kwargs)

    class ReadOnlyBackend(object):
        @staticmethod
        def DatabaseWrapper(*args2, **kwargs2):
            connection = backend.DatabaseWrapper(*args2, **kwargs2)
            connection.ops.compiler_module = readonly_compiler_module
            return connection

    return ReadOnlyBackend

# Make sure all future values will be changed too
# (this is mostly important for the real life)
utils.load_backend = custom_load_backend
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

If we follow the [original code](https://github.com/django/django/blob/9b9c8c4/django/db/utils.py#L211-L212):
* `load_backend` is called and returns an object (more precisely a module);
* in this object, a `DatabaseWrapper` is called and returns a `DatabaseWrapper` instance;
* In `DatabaseWrapper.__init__()`, it defines the `op` object whose `compiler_module` we want to change.

So we use Python duck-typing capabilities :
* Our own `custom_load_backend` needs to return an object. Instead of a module like the original function, we'll return a class;
* The returned object needs to contain an object named `DatabaseWrapper`, which is the case, but instead of a class in the original function, our object is a staticmethod;
* When that object is called, it's supposed to return the `DatabaseWrapper`. In the original function, this would simply a call to the class constructor. In our cas, it's a call to the static method. The static method will instanciate a real `DatabaseWrapper`, then patch it and then return it.

The magic of Python duck-typing is that python has no need to know that it just manipulated a class and a staticmethod instead of a module and a class like it was originally written for, because both had the same interfaces.

So now, all that's left for us to see is what exactly our `SQLCompiler` does.

## `compiler.py`, the real work

{% capture content %}{% highlight python %}
from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql.compiler import SQLInsertCompiler as BaseSQLInsertCompiler  # noqa
from django.db.models.sql.compiler import SQLDeleteCompiler
from django.db.models.sql.compiler import SQLUpdateCompiler as BaseSQLUpdateCompiler  # noqa
from django.db.models.sql.compiler import SQLAggregateCompiler

SQLCompiler = SQLCompiler
SQLDeleteCompiler = SQLDeleteCompiler
SQLAggregateCompiler = SQLAggregateCompiler
{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

The SQL compiler module is expected to contain classes named in a very specific way. The classes that we're not modifying, we'll just import them and don't touch them.

For the ones we'll modify, we'll actually subclass them and add the a mixin that reads as follow:

{% capture content %}{% highlight python %}
class ReadonlySQLCompilerMixin(object):

    @property
    def readonly_field_names(self):
        try:
            readonly_meta = getattr(self.query.model, "ReadonlyMeta")
        except AttributeError:
            return ()
        else:
            fields = getattr(readonly_meta, "_cached_readonly", None)
            if not fields:
                readonly_meta._cached_readonly = fields = frozenset(
                    getattr(readonly_meta, "readonly", ()))
            return fields

    def as_sql(self):
        readonly_field_names = self.readonly_field_names
        if readonly_field_names:
            self.remove_readonly_fields(readonly_field_names)
        return super(ReadonlySQLCompilerMixin, self).as_sql()


{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

The `readonly_field_names` will explore the Model associated to the query, and if there's a class named `ReadonlyMeta` defined here, it will read its `readonly` property containing the names of the fields we want to be readonly. We make a [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset) out of it, because that's the best structure Python provides for our use (unordered iterable with unique values that we never have to update in the course of the program). These field names are returned.

The `as_sql` method is the entrypoint for all things SQL, so that's where we're going to hit. Sadly, the format of the fields is not the same for `SQLInsertCompiler` and `SQLUpdateCompiler`, so we'll let the subclass add all the necessary details.

The subclasses are just doing the expected work : removing the fields from the query :

{% capture content %}{% highlight python %}
class SQLUpdateCompiler(ReadonlySQLCompilerMixin, BaseSQLUpdateCompiler):

    def remove_readonly_fields(self, readonly_field_names):
        """
        Remove the values from the query which correspond to a
        readonly field
        """
        values = self.query.values

        # The tuple is (field, model, value) where model if used for FKs.
        values[:] = (
            (field, _, __) for (field, _, __) in values
            if field.name not in readonly_field_names
        )


class SQLInsertCompiler(ReadonlySQLCompilerMixin, BaseSQLInsertCompiler):

    def _exclude_readonly_fields(self, fields, readonly_field_names):
        for field in fields:
            if field.name not in readonly_field_names:
                yield field

    def remove_readonly_fields(self, readonly_field_names):
        """
        Remove the fields from the query which correspond to a
        readonly field
        """
        fields = self.query.fields

        try:
            fields[:] = self._exclude_readonly_fields(
                fields, readonly_field_names)
        except AttributeError:
            # When deserializing, we might get an attribute error because this
            # list shoud be copied first :

            # "AttributeError: The return type of 'local_concrete_fields'
            # should never be mutated. If you want to manipulate this list for
            # your own use, make a copy first."

            self.query.fields = list(self._exclude_readonly_fields(
                fields, readonly_field_names))

{% endhighlight %}{% endcapture %}
{% include notebook-cell.html execution_count='In: [ ]' content=content type='input' %}

There's not much to say here. A few tricks are used :

* `my_list[:] = new_list` is quite the same as `my_list = new_list` except that the former re-uses the same list, while the latter creates a new list in memory.
* The 2 forms of generators are used here. The comprehension generator and the one that uses `yield`. If you don't know about those, go and learn about it, it's one of Python's really nice features.

## Conclusion

Well that's the whole of it ! We patch the compiler to remove the readonly fields from the sql requests. We do this both in the main thread and in the subthreads created afterwards. And just with this, it works.

But this is only a part of Django Readonly Field. In order for it to be usable, we need many other parts. If you're interested in other articles on, say, the tests, the CI, the scaffolding, the packaging etc, let me know !

