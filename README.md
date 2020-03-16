# Cover

Audible hostage letters.

## Installation

Cover requires Python 3.8 and the [SoundFile](https://pypi.org/project/SoundFile/) and 
[samplerate](https://pypi.org/project/samplerate/) libraries. You can install them as such:

```shell script
python3 -m pip install --user soundfile samplerate
``` 

You may need to install the Python development headers _before_ running the pip command. 
On distros using APT (Debian, Ubuntu, ...) the following should work:
```shell script
sudo apt install python3-dev
```

## Usage

```shell script
$ ./cover.py --help
usage: Rearrange a sound file to match another [-h] [--chunk-length CHUNK_LENGTH] [--seed SEED] [--max-swap-fails MAX_SWAP_FAILS] target palette out

positional arguments:
  target                the sound file to recreate
  palette               the sound file to recreate it from
  out                   the sound file to output

optional arguments:
  -h, --help            show this help message and exit
  --chunk-length CHUNK_LENGTH
                        the length of each chunk the sound files are divided in
  --seed SEED           the seed of the random number generator
  --max-swap-fails MAX_SWAP_FAILS
                        the maximum number of failed attempts to improve the quality

```

Cover requires three sound files: the target, the palette, and an output file. The target is the file that should be
recreated as closely as possible. The palette is the file where fragments or chunks are pulled from. The output file
is simply the path where the result is written to.

The algorithm also has two tweakable  parameters: the chunk length and the max swap fail count. 

The chunk length is
the amount of milliseconds each fragment should be. Longer chunks will result in a more noticable influence of the
palette. Very short chunks, of only a few milliseconds, will often yield better output quality, but will sound less
like the palette.

The max swap fail count is the maximum number of attempts the program should make to change the order of the chunks
in order to improve the output quality. If a swap succeeds, the counter is reset to zero. Because the process is random,
swaps will fail relatively often, so a max count of at least 100 is advised. After about 1000 the improvements will
no longer be noticable in most cases. 

## Supported formats

Which formats are supported by Cover is dependent on the list of formats supported by the SoundFile package, which
in turn depends on libsoundfile. You can query the list of supported formats with the following script:

```shell script
python3 -c 'import soundfile; print("\n".join(soundfile.available_formats().values()))'
```
