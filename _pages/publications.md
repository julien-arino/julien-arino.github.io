---
layout: page
permalink: /publications/
title: Publications
description: Publications by categories in reversed chronological order.
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<ul class="nav nav-tabs mt-3" id="publicationsTabs" role="tablist">
  <li class="nav-item" role="presentation">
    <a class="nav-link active" id="refereed-tab" data-toggle="tab" href="#refereed" role="tab" aria-controls="refereed" aria-selected="true">Refereed</a>
  </li>
  <li class="nav-item" role="presentation">
    <a class="nav-link" id="other-tab" data-toggle="tab" href="#other" role="tab" aria-controls="other" aria-selected="false">Other publications</a>
  </li>
</ul>

<div class="tab-content" id="publicationsTabsContent">
  <div class="tab-pane fade show active" id="refereed" role="tabpanel" aria-labelledby="refereed-tab">
    <div class="publications">
      {% bibliography --query @*[nonrefereed!=true] %}
    </div>
  </div>
  <div class="tab-pane fade" id="other" role="tabpanel" aria-labelledby="other-tab">
    <div class="publications">
      {% bibliography --query @*[nonrefereed=true] %}
    </div>
  </div>
</div>
