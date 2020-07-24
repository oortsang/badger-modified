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

#### command

One fillable argument in the submission template must be named `command`, and it must be specified. This is usually used for the main command being executed by each job. 

#### template

Specify the location of the submission template with respect to the location of the YAML file. 

#### copy_to_item 

??? TODO

#### default_arguments

If the `arguments` section doesn't specify a field which appears in the submission template, it will be filled in with a value from this list, if possible. I usually specify job resource requirements here. 

#### submission

Specify (with a tag) the type of submission queue. Currently, the only implemented tag is `!PBSQueue`. 
We hope to implement `!SLURMQueue` soon. 
Keys under this tag include `jobs_folder` which specifies the path to which the jobs will be written; `job_name_key` the argument which specifies the filename of each job (usually I use `job_name` argument); `fake_submission` which when specified and marked `true` only writes the job files but doesn't submit or execute them. 

#### constants

This is a good place to specify long reused filepaths with YAML's anchor functionality. 

#### pre_command

Specify a bash string to run before doing anything else, such as setting up result directories. Don't worry about setting up the folders for `jobs_folder` or `logs_folder`. 

### Arguments

There are a bunch of ways to specify arguments. For an exhaustive list, go to the wiki. Here, we'll talk about Scalars, which are the same for each job, Range, which specifies a range of integers, and FilesInFolder, which creates a new argument for each file in a folder. 

There are often multiple dynamic arguments specified. In the `example_submission.yaml`, we see two different Ranges specified. Badger's default behavior is to create one job for each unique element in the cartesian product of these dynamic argument sets. For `example_submission.yaml`, that means that there is one job for each (`chromosome`, `batch`) pair, or 220 total jobs.

#### !Scalar

These arguments stay the same for each job. The `name` key defines where in the template this argument should go, `prefix` and `value` allow you to separate the command-line flag from its value. `prepend` works for file paths, and it makes a neat filepath with `prepend` before `value`. 

#### !Range

These arguments form a range of integers. Besides the things that can be specified for `!Scalar`, one must specify `start` and `end`. 

#### !FilesInFolder

This creates a list of files in a specific folder. Be sure to specify `folder`. One neat functionality is to specify `regexp_filter`. Only matched filenames will be added to the list. What's more, if there are capture groups specified in the regex, these groups can be saved in the metadata (More about that in the wiki). 

## Run Badger

Try it out for yourself! In this directory, you can run:

```bash
python src/badger.py \
-yaml_configuration_file examples/example_submission.yaml \
-parsimony 9
```
And see the output! This should create 220 files inside a newly-created `jobs` folder. 