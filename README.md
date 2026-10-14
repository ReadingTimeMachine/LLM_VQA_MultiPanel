# Do you “see” what I “see”? A Multi-panel Visual Question and Answer Dataset for Large Language Model Chart Analysis

Welcome to the repository for the paper "Do you “see” what I “see”? A Multi-panel Visual Question and Answer Dataset for Large Language Model Chart Analysis", presented at TPDL 2026 (this will be updated with links when applicable).

<!--
<div align="center">
  <a href="TBD"><img src="https://img.shields.io/badge/Paper-arXiv-red" alt="arXiv"></a>
  <a href="https://huggingface.co/datasets/ReadingTimeMachine/visual_qa_multipanel"><img src="https://img.shields.io/badge/Dataset-%F0%9F%A4%97%20Hugging_Face-yellow" alt="Hugging Face"></a>
  <a href="TBD"><img src="https://img.shields.io/badge/JCDL-2025-blue" alt="JCDL 2025"></a>
</div>
-->

<div align="center">

 <a href="https://arxiv.org/abs/2610.14173"><img src="https://img.shields.io/badge/Paper-arXiv-red" alt="arXiv"></a>
  <a href="https://huggingface.co/datasets/ReadingTimeMachine/visual_qa_multipanel"><img src="https://img.shields.io/badge/Dataset-%F0%9F%A4%97%20Hugging_Face-yellow" alt="Hugging Face"></a>
<a href="https://tpdl2026.ualg.pt/program/"><img src="https://img.shields.io/badge/TPDL-2026-blue" alt="TPDL 2026"></a>
</div>


## Overview

Multi-panel figures make up 30-60% of the figures in scientific literature, but they are hard to
benchmark: for a figure pulled from a real paper, the "right" answer to a question about
a specific panel is rarely known exactly.  Here, we generate synthetic multi-panel figures and include the original data along with figure bounding box information.  We include a set of questions answered from the figure's data for Visual Question and Answering (VQA) tasks.


The pipeline has four stages:

1. **Generate figures.** Synthetic multi-panel figures are drawn at random --
   panel grids, aspect ratios, plot styles, colormaps, fonts, titles/axis labels
   (including LaTeX math), and the underlying data -- with distributions of layout
   parameters informed by figures found in real arXiv papers.  Each figure is saved as
   an image plus a JSON file recording everything that went into it.  Supported panel
   types are **line**, **scatter**, **histogram**, and **contour** plots.
2. **Build QA pairs.** The ground-truth JSONs are converted into questions and
   answers, each tagged with a complexity level taken from the accessibility framework of [Lundgard 2022](https://pubmed.ncbi.nlm.nih.gov/34591762/).  Questions are asked in a
   "respond only in JSON" format so the answers can be parsed and scored automatically.
   * *Level 1* -- counting and identification: how many panels, plot types, plotting
     style, colormap, aspect ratio, titles, axis labels, tick labels, number of
     lines/points/bars, line styles.
   * *Level 2* -- data value extraction: minimum, maximum, mean and median along the
     x/y/color axes of a given panel, presence of error bars.
   * *Level 3* -- relationships and reasoning: what functional form the data follows
     (random / linear / Gaussian mixture), and cross-panel questions that require
     comparing panels to each other (e.g. which panel has the strongest relationship,
     or the largest median).

   Questions are additionally split by scope into *figure-level* (about the figure as a
   whole) and *plot-level* (about one identified panel), which is where multi-panel
   reasoning gets interesting -- a model has to first locate the right panel before it
   can answer.
3. **Query the models.** The image and its question list are sent through the
   OpenAI, Anthropic and Google Gemini APIs, with and without extended
   reasoning/thinking budgets, and the raw responses are cached to disk.
4. **Score and plot.** Responses are parsed back out of (sometimes malformed) JSON,
   aligned against the ground truth, and scored -- exact/approximate match for counts
   and categories, CER/Levenshtein distance for text such as titles and labels, and
   symmetric relative error for extracted numeric values.  The scored results become
   the accuracy figures and tables in the paper.

The dataset itself is published on
[Hugging Face](https://huggingface.co/datasets/ReadingTimeMachine/visual_qa_multipanel);
this repository is the code that produces and analyzes it.

## Important Files

### Figure and dataset generation

| File | What it does |
|---|---|
| [create_figures_batch.py](create_figures_batch.py) | Main entry point for generating the synthetic figures.  Writes images, ground-truth JSONs, pickles and diagnostic plots to `-save_dir`.  Runs in parallel, e.g. `mpirun -np 4 python create_figures_batch.py -save_dir <dir> -number_of_figures 200`. |
| [create_vqa_from_datas.ipynb](create_vqa_from_datas.ipynb) | Run after `create_figures_batch.py`: turns the ground-truth JSONs into the Level 1/2/3 question-and-answer JSONs that make up the dataset. |
| [examine_batched_figures.ipynb](examine_batched_figures.ipynb) | Sanity checks and statistics over a generated batch of figures (including title/label stats). |
| [trial_cross_panel.ipynb](trial_cross_panel.ipynb) | Scratch space for prototyping new cross-panel questions before they are added to the QA generation. |
| [create_simple_figure_clusters.ipynb](create_simple_figure_clusters.ipynb) | Defines visual "clusters" of similar figures, used to measure how visually distinct the generated figures are from each other. |

### Querying the models

| File | What it does |
|---|---|
| [chatgpt/chatgpt_withapi.ipynb](chatgpt/chatgpt_withapi.ipynb) | Sends the VQA pairs to OpenAI models (including high-reasoning / low-verbosity and mini variants). |
| [claude/claude_withapi.ipynb](claude/claude_withapi.ipynb) | Sends the VQA pairs to Anthropic Claude models, with optional thinking and a configurable thinking-token budget. |
| [gemini/gemini_withapi.ipynb](gemini/gemini_withapi.ipynb) | Sends the VQA pairs to Google Gemini models, with optional thinking budget. |
| [gemini/gemini_withapi_qualitative.ipynb](gemini/gemini_withapi_qualitative.ipynb) | The same, but for the open-ended qualitative "describe this figure" analysis. |
| [qualitative_prompts.ipynb](qualitative_prompts.ipynb) | Samples random multi-panel figures and builds the prompts used for the qualitative analysis. |

Each of these notebooks caches one pickle per figure of prompts, ground-truth answers
and raw model responses, so runs can be restarted without re-paying for completed
queries.

### Parsing results and making paper figures

| File | What it does |
|---|---|
| [parse_lmm_outputs_to_kde_and_scatter_plots.ipynb](parse_lmm_outputs_to_kde_and_scatter_plots.ipynb) | The main analysis notebook: loads every model's cached responses, aligns them with ground truth, and produces the accuracy comparisons across models, levels and question types. |
| [figure_notebooks/counting_types_figure.ipynb](figure_notebooks/counting_types_figure.ipynb) | Counting and plot-type accuracy figure. |
| [figure_notebooks/cer_titles_figure.ipynb](figure_notebooks/cer_titles_figure.ipynb) | Character-error-rate results for titles and axis labels. |
| [figure_notebooks/mean_med_calcs_figure.ipynb](figure_notebooks/mean_med_calcs_figure.ipynb) | Accuracy of extracted mean/median values, and the definition of the relative-error metric used in the paper. |
| [figure_notebooks/calculate_cost.ipynb](figure_notebooks/calculate_cost.ipynb) | Estimates the API cost of running the benchmark per model. |
| [figure_notebooks/other_datasets_table.ipynb](figure_notebooks/other_datasets_table.ipynb) | Builds the comparison table/chart of this dataset against other chart-QA datasets. |

### Supporting modules

| Path | What it does |
|---|---|
| [utils/main_plot_utils.py](utils/main_plot_utils.py) | `make_random_plot()` -- the figure generation loop: draws a figure, extracts its ground truth, and retries on failure. |
| [utils/figure_class.py](utils/figure_class.py) | `FigureRun`, the container for a single figure's random seeds, layout, font and style parameters. |
| [utils/misc_utils.py](utils/misc_utils.py), [utils/misc_plot_utils.py](utils/misc_plot_utils.py) | Layout helpers, including the arXiv-derived aspect-ratio and row/column distributions and the grouping of detected panel boxes into a grid. |
| [utils/plot_qa_utils.py](utils/plot_qa_utils.py) | Shared question-construction machinery: QA skeleton, persona/context strings, panel-index phrasing, and the JSON output-format instructions. |
| [utils/figure_level_qa_utils.py](utils/figure_level_qa_utils.py) | Figure-level questions (panel count, style, colormap, aspect ratio, titles, labels, tick labels, plot types). |
| `utils/{linear,scatter,histogram,contour}_plot_qa_utils.py` | Per-panel-type questions for line, scatter, histogram and contour plots. |
| [utils/general_plot_level_qa_utils.py](utils/general_plot_level_qa_utils.py) | Plot-level questions that apply regardless of panel type (e.g. error bars). |
| [utils/cross_panel_qa_utils.py](utils/cross_panel_qa_utils.py) | Cross-panel questions requiring comparison between panels. |
| [utils/llm_utils.py](utils/llm_utils.py) | Shared API-side helpers: image loading/resizing and encoding, pairing images with their QA JSONs, prompt assembly, and error detection in responses. |
| [utils/parse_lmm_output_utils.py](utils/parse_lmm_output_utils.py) | Recovering JSON from model output (including LaTeX-escape repair), matching model answers to ground truth, and the comparison metrics. |
| [utils/results_plotting_utils.py](utils/results_plotting_utils.py), [utils/latex_utils.py](utils/latex_utils.py) | Accuracy calculations, KDE/grid plotting helpers, and LaTeX table formatting for the paper. |
| [synthetic_training_figures/utils/](synthetic_training_figures/utils/) | Lower-level figure-generation library: data distributions, plot classes, text/LaTeX generation, pixel-location and metric utilities. |
| [yt/](yt/) | Vendored parallelism utilities borrowed from [yt](https://yt-project.org/), used for the MPI-parallel figure generation. |


## Known Issues

1. For Claude -- token limits mean there are some issues for multi-panel plots, specifically for x/y tick values

## Citation information

If you use this work please cite:
```
Accepted to TPDL, 2026.  Link to be added shortly.
```
