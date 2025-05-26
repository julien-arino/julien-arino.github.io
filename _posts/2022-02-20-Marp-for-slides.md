---
layout: post
title:  "Using Marp to make cool html presentation slides"
description: "How to use Marp to make nice looking presentation slides, from the perspective of an only-partly-savvy computer user."
date:   2022-02-20
categories: presentations
---

For the file links, skip directly to the end of this post.

# General context

Giving presentations about my research work is something I seem to do quite a lot. Perhaps because my MSc supervisor was a physician who put great emphasis on slide content and form, I have always spent a lot of time on my presentation files. I am often asked to give talks about my work on the spatio-temporal spread of infectious diseases using metapopulations; however, except in rare instances such as giving three times the same talk in three different universities over the course of two days, I always try to change things between two talks even if they have the same title. There is always something that did not flow well, some typo that appeared, some new idea to throw in, etc.

All that to say: finding the good tool for preparing presentations has been an ongoing project. 

Let me start with the elephant in the room: I avoid like the plague tools like PowerPoint or LibreOffice Impress. This is a consequence of the epoch at which I started giving talks: back in the late 1990s, PowerPoint did very poorly with mathematics and only a few brave souls used it in talks.

For efficiency, using a LaTeX based approach always seemed the best. You can copy and paste your content directly from your papers, thereby saving a lot of time. While it is possible to hack together a presentation, it is easier to use existing packages and through the years, I used several different tools.

- `inriaslides`, back when I was working on my PhD at.. INRIA (now [Inria](https://www.inria.fr/en/inria-centre-universite-cote-azur)).
- After I left Inria in 2001, it became silly to use their slide package (which put the logo everywhere, etc.) and so for a while, I actually used a simple model that I came up with. Key word being *simple*. I used this for about 2 years.
- In 2003, I started using [`prosper`](https://ctan.org/pkg/prosper), which was a major step forward for LaTeX slides.
- Then, in the summer of 2005, I stumbled upon [`Beamer`](https://ctan.org/pkg/beamer). `Beamer` was a revolution, because you compile your text directly using `pdflatex` instead of having to run through a sequence of conversions like with `prosper`.

# Beamer and the joys of embedding movies

`Beamer` is great, but one of the major headaches has always been the inclusion of movies in the `pdf` files generated. It was a pain, but with the retirement of `flash` support at the beginning of 2021, this became completely impossible. I do not embed that many movies, but it happens often enough that I need a reliable and not too complicated way of doing so.

# Marp

With the "death" of the flash route for embedding movies, I looked for other ways to generate files potentially involving movies. As part of my using `Rmarkdown`, I have become quite a fan of `markdown`, so when I found [Marp](https://marp.app/), I decided to give it a shot.

One word of warning, first: Marp is developed by programmers who, I think, have not yet understood that with the proper support for LaTeX (see later) and the defection of people like me from the `Beamer` ecosystem, some of their newer users are not programmers. For now, requests for help are often answered promptly but not very helpfully from the perspective of a non-specialist. This is part of the reason for my making my markdown files accessible together with rendered html and pdf files of the presentations I will post.

## Running Marp

It is possible to install a command line version of Marp and this is the way to achieve the best results, but I find that the Visual Studio Code extension does a good enough job for my usage and that is what I use most often. You can preview what you type as you are typing it and can then easily export to `html`, `pdf` or PowerPoint.

## Writing slides

The main thing to know is that your file needs to contain a `YAML` header to set a few properties of the document and separates `markdown` containing slides by `---` markers. And can include mathematics.

- **YAML header**. This is where you define such things as the title that will appear in the browser tab (in the case of an `html` render), the slides form factor, inclusions, etc.
- **Separate slides with ---**. Beware to leave an empty line after and above the separators.
- **Markdown content**. That makes things very easy.
- **Mathematics support**. Probably the most important characteristic for modellers. Marp allows to choose whether you use [MathJax](https://www.mathjax.org/) or [KaTeX](https://katex.org/), with KaTeX used by default. KaTeX seems to be faster than MathJax and is quite similar in practice to MathJax anyway. The biggest difference in my recent experience is that 

```
\begin{align*}
x & xx \\
y & yy 
\end{align*}
```

<ul class="list-unstyled">
needs to be typeset as
</ul>
```
$$
\begin{aligned}
x & xx \\
y & yy 
\end{aligned}
$$
```

<ul class="list-unstyled">
as KaTeX in Marp does not recognise ``\begin{align*}`` and similar environments. So porting LaTeX to Marp sometimes involves a little bit more work than when porting to Beamer, but this remains easy.
</ul>

## Additional styling elements
Note that it is possible to use `html` or `css` constructs in the code to obtain results that are more elaborate than what is allowed by basic `markdown`. This goes a bit against the philosophy that underlies LaTeX and `markdown`, but is useful.


# Where to find my presentation files

[Update 2022-02-27] To finish, files are available from [this GitHub repository](https://github.com/julien-arino/presentations). They can be seen in several format.

- The `markdown` files, `pdf` and raw `html` files, as well as the figure and movie files, are located in the repo.
- The `html` files can be viewed in a browser by instead following the link to the GitHub pages [version of the repo](https://julien-arino.github.io/presentations/).
- 
