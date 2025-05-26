---
layout: post
title:  "Mathematical epidemiology in a data-rich world"
description: "Comments on and Rmarkdown source code of the paper Mathematical epidemiology in a data-rich world (Infectious Diseases Modelling, 2020)."
date:   2020-01-15
categories: r-code data simulation
---
Find the code [here](https://github.com/julien-arino/modelling-with-data).

This post contains some information about the paper [Mathematical epidemiology in a data-rich world](https://doi.org/10.1016/j.idm.2019.12.008), [*Infectious Disease Modelling*](https://www.sciencedirect.com/journal/infectious-disease-modelling) **5**: 161-188, 2020.

The aim of the paper is to provide some ideas about the acquisition and use, in mathematical epidemiology models, of data originating from open data sources.

The paper is part of a special issue on [*Confronting Infectious Disease Models with Public Health Data*](https://www.sciencedirect.com/journal/infectious-disease-modelling/special-issue/10Z42V1KN0Q), edited by [Michael Li](https://sites.ualberta.ca/~myli/), [Junling Ma](https://www.math.uvic.ca/~junlingm/dokuwiki/doku.php), [Zen Jin](https://www.researchgate.net/profile/Zhen_Jin/info) and myself.

The paper was supposed to come with an electronic appendix, which at present is not included. Also, some edition related quirks were added because of the journal style, with in particular, the `R` code appearing as images rather than text and therefore not being selectable. As a consequence, I have made a copy available as a GitHub repository ([here](https://github.com/julien-arino/modelling-with-data)). My plan is to keep the file there up to date if links given in the paper were to change.

## Writing a scientific paper in `Rmarkdown`
While I have been using `Rmarkdown` for a while to generate reports about some of the work I do in the context of the global spread of infectious diseases, I had never actually tried to produce a proper paper using this model. Here are some recommendations based on experience developed in the process.

1. Save a local copy of your data. Keep in mind that you could end up editing your file while onboard a plane with no wifi, or in a country that filters some sites or who knows what. In any event: with poor or inexistent Internet access. The method I have used in the paper is to include all Internet-based requests within tests and set a global variable `DOWNLOAD` that indicates where the data should be downloaded from the web (`TRUE`) or if the local cache should be used (`FALSE`).
2. Producing a pdf is easy; using a publisher's tex style is not as easy. For now, I have only included a stripped down version of my `Rmarkdown` file that should work out of the box. I will later include in the repository the file that uses the Elsevier document class `elsarticle`.

**Update 2022-02-15** Because of work on COVID-19 response, I have not posted anything in over two years. For an upcoming summer school, I have to revisit some work on the use of data scraped from Internet and in particular, ensure that the code still works. The revised code is still located [here](https://github.com/julien-arino/modelling-with-data) and supersedes the old code.