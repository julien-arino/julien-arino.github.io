---
layout: page
permalink: /publications/
title: publications
description: Publications in reverse chronological order. Generated by jekyll-scholar.
nav: true
---

<!-- _pages/publications.md -->
<!-- From https://github.com/inukshuk/jekyll-scholar/issues/157 -->

<div class="newpublications">

{% capture numJournalPapers %}
  {% bibliography_count %}
{% endcapture %}
<div style="counter-reset:bibitem {{numJournalPapers|plus:1}}">
</div>
{% bibliography --group_by year --group_order descending %}

</div>