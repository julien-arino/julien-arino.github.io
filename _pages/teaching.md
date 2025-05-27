---
layout: page
title: teaching
permalink: /teaching/
description: Material for some courses both current or recent and past. For ongoing courses, information specific to a term is on UMLearn.
nav: true
display_categories: [recent, older]
horizontal: false
---

<!-- pages/teaching.md -->
<div class="projects">
{%- if site.enable_teaching_categories and page.display_categories %}
  <!-- Display categorized teaching -->
  {%- for category in page.display_categories %}
  <h2 class="category">{{ category }}</h2>
  {%- assign categorized_teaching = site.teaching | where: "category", category -%}
  {%- assign sorted_teaching = categorized_teaching | sort: "importance" %}
  <!-- Generate cards for each teaching -->
  {% if page.horizontal -%}
  <div class="container">
    <div class="row row-cols-2">
    {%- for teaching in sorted_teaching -%}
      {% include teaching_horizontal.html %}
    {%- endfor %}
    </div>
  </div>
  {%- else -%}
  <div class="grid">
    {%- for teaching in sorted_teaching -%}
      {% include teaching.html %}
    {%- endfor %}
  </div>
  {%- endif -%}
  {% endfor %}

{%- else -%}
<!-- Display teaching without categories -->
  {%- assign sorted_teaching = site.teaching | sort: "importance" -%}
  <!-- Generate cards for each teaching -->
  {% if page.horizontal -%}
  <div class="container">
    <div class="row row-cols-2">
    {%- for teaching in sorted_teaching -%}
      {% include teaching_horizontal.html %}
    {%- endfor %}
    </div>
  </div>
  {%- else -%}
  <div class="grid">
    {%- for teaching in sorted_teaching -%}
      {% include teaching.html %}
    {%- endfor %}
  </div>
  {%- endif -%}
{%- endif -%}
</div>
