# Abstract

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jrladd/edge-cases-JDH/main?filepath=article-text.ipynb)

This article will explore the role of network analysis research tools as/in scholarly infrastructure, and also detail our attempt to intervene in these practices by building *Network Navigator*, a browser tool for network analysis. In making *Network Navigator*, we intentionally contributed to an existing ecosystem of network analysis tools, namely *Gephi* and *Palladio*, but we were also motivated to combine the principles of minimal computing with new developments in web architecture and DH. We believe our perspective helps complicate our understanding of “tool”-building, making visible the obscured interpretive work of DH infrastructure. Given the centrality of GUI tools in introductory DH pedagogy, we believe that the making and maintaining of DH tools remains one of the profoundly influential, and yet consistently under theorized, areas of DH scholarship and teaching. Even as tools seem to be so foundational to DH, at the same time they remain rarely debated or even defined as a category. Rather than treating ‘tools’ as simply technical objects, we want to critically examine how their design and materiality directly shapes this conceptual amorphousness, but also more profoundly how this definitional problem makes it difficult to discern the ways DH tools are determining larger DH systems and infrastructure.

# Keywords
NetworkAnalysis, Networks, Visualization, Tools, DH

## Installation Instructions

This notebook relies on the following packages:
- `cite2c==2.31.0` for citation
- `jupyter-contrib-nbextensions==0.5.1` for table of contents

These dependencies require Python 3.6 to 3.8, so you will likely need to revert your Python version to run this notebook. This also causes a number of dependency conflicts, so we recommend using a virtual environment to run this notebook.

We do have a `requirements.txt` file for installation, but given this larger dependencies issues, we cannot guarantee that it will work as a means to install dependencies. So we have also included a list of our libraries that you will need to install below, in addition to libraries for jupyter notebooks:

```bash
altair vega nltk statsmodels pandas numpy matplotlib wordcloud scikit-learn networkx
```

