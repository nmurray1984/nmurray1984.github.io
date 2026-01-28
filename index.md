---
title: Home
---

## About

I'm Nathan Murray. Welcome to my personal website where I share my thoughts, projects, and writing.

---

## Articles

{% if site.posts.size > 0 %}
<ul class="post-list">
{% for post in site.posts %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %d, %Y" }}</time>
  </li>
{% endfor %}
</ul>
{% else %}
*No articles yet.*
{% endif %}
