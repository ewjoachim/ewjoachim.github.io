---
title: "Django Readonly Field - Chapter 1 - The lib"
icon: book
date: 2016-10-22 00:00:00
---

[Django Readonly Field](https://github.com/novafloss/django-readonly-field) is a tiny Django library to make sure Django never tries to write certain model fields. and the introduction to the series of articles.

{{ excerpt_separator }}

# The problem

You are using a Postgresql database to power you Django website, and you'd like to use certain features that make this database great like, say, materialized views, or triggers. In other words, you're saying that there are some specific  fields in some specific tables of your database that are completely OK to read and absolutely not ok to write.

That's perfect because there's a property of Django Model Fields that is called ["editable"](https://docs.djangoproject.com/en/1.10/ref/models/fields/#editable) that keeps those fields from being included in Model forms. Yay, problem solved.

## Except...

You have no control over what the ORM will do. Especially, when you do a `model.save()`, those field will be written to the database (even if they have not changed and especially if they did). If you happen to have a large codebase, it can be tricky to manually audit all of your code (both past and future) to make sure that no one will ever write on this field.

So let's take a different approach.

# The solution

## The short answer

Use [django-readonly-field](https://github.com/novafloss/django-readonly-field). It's quite young I admit, but it's tested, it's simple and I wrote it.

Once you've configured what fields you want to be read only, Django will never ever include those field in `INSERT` and `UPDATE` queries.

I don't really want to copy the usage instruction because it's already in the Readme, but, trust me, it's dead simple.

## The longer answer _(a.k.a how does this work ? Is this black magic ?)_

In the Era of the Geek, we're all magicians here, the only difference is that many of us tend to open source our tricks. But the source is not in itself the key to understanding all that takes place here without at least a bit of information.

So, there's [a second article]({% post_url 2016-10-22-django-readonly-field-2-code %}) that explain how it works. I might continue the series and explain more things like the tests, the scaffolding, the CI, the packaging etc, depending of the feedback (if any).

Thank you, and stay tuned !
