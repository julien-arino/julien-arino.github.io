---
layout: post
title:  "Some useful Marp stuff"
description: "Compendium of commands useful in Marp: two columns, centering figures, formatting theorems, etc."
date:   2022-03-17
categories: presentations
---

I posted some time back about using Marp to make presentations (see [here](https://julien-arino.github.io/blog/2022/Marp-for-slides/)). In keeping with the idea that this blog is mostly for myself as a space to store stuff that is useful to me, here is a compendium of commands that I have found useful when preparing slides using Marp. I will edit this post regularly as I discover new tricks, rather than create another entry.

As I mentioned in my original post about Marp, there is a gap between the way Marp is documented and my capacity to understand said documentation, but altogether: going further than what is doable using straight markdown is going to require using html/css code. So what follows is mostly in these formats. Note also that I am detailing stuff that works within Visual Studio Code, not using the command line version of Marp. The latter is more powerful and versatile but does not fit my current workflow.

## Using multiple columns of text

To generate the equivalent of a `minipage` in Beamer, you can use the following code.

{% highlight html %}
<style scoped>
@import url('https://unpkg.com/tailwindcss@^2/dist/utilities.min.css');
</style>
<div class="grid grid-cols-2 gap-4">
<div>

Content of first column
</div>

<div>

Content of second column
</div>
</div>
{% endhighlight %}

Two remarks. Firstly, the place where I got the code advocated for placing the import statement in the `yaml` header, something like  

```
---
marp: true
-style: @import url('https://unpkg.com/tailwindcss@^2/dist/utilities.min.css');
---
```

but I found that this results in a massive (1 MB) html file. Secondly, in the same spirit, I am using `<style scoped>` to say that this only applies to the current slide. Removing the keyword `scoped` would imply that all subsequent slides have access to the `grid grid-cols-2 gap-4` class. With, I imagine, the same code bloating. (Untested at this time.)

## Centering figures

Another frustration when switching from Beamer to Marp is that there is no easy `\begin{center}` type command to center a figure in Marp. A variety of ways are available, but I found that the one that is easiest is to include something like

{% highlight html %}
<style>
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>
{% endhighlight %}

somewhere in your slides. Using `<style>` without the keyword `scope` means that the style is defined once and for all, so I put this at the end of my title page and forget about it. Once this is done,

```
![width:200px center](image_file.png)
```

will center the figure.

## Boxes for definitions, theorems, etc.

Another one of these Beamer classics that is difficult to do in Marp.

{% highlight html %}
<div align=justify 
style="background-color:#16a085;
border-radius:20px;
padding:10px 20px 10px 20px;
box-shadow: 0px 1px 5px #999;">

Some beautiful theorem (make sure to leave an empty line above the first line
of text if you want markdown to work).
</div>
{% endhighlight %}

Now, here I have not done my homework: surely, there is a way to define this as a style, and it is likely that a future update of this blog post will have this. For the time being, I just copy and paste this code wherever I need it, changing the colour for definitions, etc.

## Numbering equations and referring to them

This is my biggest frustration so far with using Marp. In many talks, I do not really care for this, but as part of a course that I am preparing (more on this in another post), I really need equation numbers. Whether it is MathJax or KaTeX, support for equation numbers is still sketchy altogether, but I find that Marp adds one level of complication. What I have managed to make work, at present, goes thusly. 

- Switch the LaTeX interpreter from KaTeX to MathJax.
- Manually (grr) tag the equations with the number you want. Note the `\qquad` commands on the first line: if you do not use them in an `align` type environment, the equation numbers will be over the equations themselves.

{% highlight latex %}
$$
\begin{align}
S' &= d(N-S)-f(S,I,N)+\nu R\qquad\qquad \tag{8a}\label{sys:SLIR_dS}\\
L' &= f(S,I,N) -(d+\varepsilon)L \tag{8b}\label{sys:SLIR_dL} \\
I' &= \varepsilon L -(d+\gamma)I \tag{8a}\label{sys:SLIR_dI} \\
R' &= \gamma I-(d+\nu)R \tag{8d}\label{sys:SLIR_dR}
\end{align}
$$
{% endhighlight %}

- Use `$\eqref{sys:SLIR_dL}$` to refer to, say, the second equation. Yes, the dollar signs need to be there..

Yes, this is bad. It is particularly bad, actually, because I like the `subequations` environment and this is supported in neither KaTeX nor MathJax. I am hopeful that things will evolve in the future and will update this post if I find better ways to do this, but for now, this seems to be the way to do it.

Remark that if you are not after a `subequations` type numbering, then you can do

{% highlight latex %}
$$
\label{sys:SLIR}
\begin{align*}
S' &= d(N-S)-f(S,I,N)+\nu R\qquad\qquad \\
L' &= f(S,I,N) -(d+\varepsilon)L \\
I' &= \varepsilon L -(d+\gamma)I \\
R' &= \gamma I-(d+\nu)R
\end{align*}
$$
{% endhighlight %}

This is a bit better. But no `subequations`..