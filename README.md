# badger

badger is a tool to generate and automate job submission on an HPC cluster. It was initially conceived and created by Alvaro Barbeira [@Heroico](https://github.com/Heroico). He created it while working in Haky Im's [lab](http://hakyimlab.org/) at the University of Chicago.

# TODO:

1. Documentation
    1. Main README
    1. Document Features in the Wiki
    1. Make an educated guess about the header for the example SLURM submission.
    1. Make an example submission YAML
1. SLURM compatibility
1. Controlled "Naive submission"
1. `ensure_paths` option for arguments
1. Test

# Instructions

First, you'll want to do some awesome science. 
This will hopefully get you to a point where you need to run a computational experiment. 
Maybe you need to test an algorithm across a range of hyperparameters; maybe you need to do some intense file-reformatting for a lot of files. 
The main use-case for badger when there are a large number of computational tasks that all need to be executed in a similar way. 

## When a project is ready for badger

Before scaling up to a parallel submission on an HPC cluster, we recommend making sure the code runs as expected on the real data in a batch (non-interactive) submission. This is akin to making sure the first element of the batch of submissions works well. 

## Creating a submission template

Once there is a working script, it is pretty easy to generalize this back to a submission template. 
We use [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) as the template engine. Notice that fillable parameters are inside double braces: `{{ parameter_name }}` and if we want braces to appear in the generated script, we use jinja2's `{% raw %}` as in `{% raw %}${PBS_JOBNAME}.e${PBS_JOBID}.err{% endraw %}`. 
Check out the example submission templates inside `examples`. 

## Specify submission parameters

We use YAML files to specify submission parameters. 
It may be most helpful to see the submisson example inside `examples`. 

The two main headings in the YAML file should be `definitions` and `arguments`.

The following will be a brief introduction to the required parts of the YAML file. There are also a lot of ways to specify arguments, and we will go through 2 common cases here, and defer the rest of the argument specification to the wiki. 

### Definitions

The definitions specify important metadata parts of the submission, such as logging paths, the type of HPC submission cluster, preparation commands, etc. 

