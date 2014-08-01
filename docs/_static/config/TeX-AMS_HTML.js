/* -*- Mode: Javascript; indent-tabs-mode:nil; js-indent-level: 2 -*- */
/* vim: set ts=2 et sw=2 tw=80: */

/*************************************************************
 *
 *  /MathJax/unpacked/config/TeX-AMS_HTML.js
 *  
 *  Copyright (c) 2010-2014 The MathJax Consortium
 *
 *  Part of the MathJax library.
 *  See http://www.mathjax.org for details.
 * 
 *  Licensed under the Apache License, Version 2.0;
 *  you may not use this file except in compliance with the License.
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 */

MathJax.Hub.Config({
  extensions: ["tex2jax.js","TeX/noErrors.js","TeX/noUndefined.js","TeX/AMSmath.js","TeX/AMSsymbols.js", "HTML-CSS/handle-floats.js"],
  jax: ["input/TeX","output/HTML-CSS"],
  showMathMenu: false
});

MathJax.Ajax.loadComplete("[MathJax]/config/TeX-AMS_HTML.js");
