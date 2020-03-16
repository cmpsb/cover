#!/usr/bin/env python3

import argparse
import sys
import math
from typing import List
import random
import numpy
import soundfile
import samplerate as libsamplerate
import progressbar


def divide_sound_file(data: numpy.ndarray, samples_per_chunk: int):

    return [
        data[i * samples_per_chunk:(i + 1) * samples_per_chunk]
        for i in range(0, math.ceil(len(data) / samples_per_chunk))
    ]


def stretch_palette(chunks: List[numpy.ndarray], num_chunks: int):
    # print([sqrt_hlen - math.fabs(sqrt_hlen - math.sqrt(i)) for i in range(0, len(chunks))])
    n = math.floor(math.log2(num_chunks))
    excess = len(chunks) - num_chunks
    if excess > 0:
        snip = excess // 2
        print(snip)
        chunks = chunks[snip:len(chunks)-snip]

    hlen = len(chunks) / 2

    weights = [math.sqrt(hlen - math.fabs(hlen - i) + 1) for i in range(0, len(chunks))]
    return random.choices(chunks, weights=weights, k=num_chunks)


def main():
    parser = argparse.ArgumentParser('Rearrange a sound file to match another')
    parser.add_argument('target', type=str, help='the sound file to recreate')
    parser.add_argument('palette', type=str, help='the sound file to recreate it from')
    parser.add_argument('out', type=str, help='the sound file to output')
    parser.add_argument('--chunk-length', type=int, help='the length of each chunk the sound files are divided in',
                        default=5)
    parser.add_argument('--seed', type=int, help='the seed of the random number generator')
    parser.add_argument('--max-swap-fails', type=int, default=250,
                        help='the maximum number of failed attempts to improve the quality')
    args = parser.parse_args(sys.argv[1:])

    random.seed(args.seed)

    target_data, target_samplerate = soundfile.read(args.target, always_2d=True, dtype='float32')
    palette_data, palette_samplerate = soundfile.read(args.palette, always_2d=True, dtype='float32')

    if palette_samplerate != target_samplerate:
        print('Resampling palette...')
        progress_bar = progressbar.ProgressBarThread()
        progress_bar.start()

        resampler = libsamplerate.Resampler(libsamplerate.converters.ConverterType.sinc_best, channels=2)
        palette_data = resampler.process(palette_data, target_samplerate / palette_samplerate)

        progress_bar.stop()

    sample_rate = target_samplerate
    del target_samplerate
    del palette_samplerate

    print('Chopping up sound files...')
    progress_bar = progressbar.ProgressBarThread()
    progress_bar.start()

    samples_per_chunk = sample_rate * args.chunk_length // 1000
    target_chunks = divide_sound_file(target_data, samples_per_chunk)
    palette_chunks = divide_sound_file(palette_data, samples_per_chunk)

    progress_bar.stop()

    print('Moulding palette...')
    progress_bar = progressbar.ProgressBarThread()
    progress_bar.start()

    # occ = {}
    result_chunks = stretch_palette(palette_chunks, len(target_chunks))
    assert len(result_chunks) == len(target_chunks)

    progress_bar.stop()

    print('Normalizing chunks...')
    progress_bar = progressbar.ProgressBarThread(2 * len(target_chunks))

    for i, chunk in enumerate(target_chunks):
        length, num_channels = chunk.shape
        if length < samples_per_chunk:
            target_chunks[i] = numpy.append(chunk, [[0, 0]] * (samples_per_chunk - length), axis=0)
            assert target_chunks[i].shape == (samples_per_chunk, 2)
        progress_bar.progress(i)

    for i, chunk in enumerate(result_chunks):
        length, num_channels = chunk.shape
        if length < samples_per_chunk:
            result_chunks[i] = numpy.append(chunk, [[0, 0]] * (samples_per_chunk - length), axis=0)
            assert result_chunks[i].shape == (samples_per_chunk, 2)
        progress_bar.progress(i)

    progress_bar.stop()

    print('Maximizing sound quality...')
    progress_bar = progressbar.ProgressBarThread(args.max_swap_fails)
    progress_bar.start()

    num_failed_swaps = 0
    num_failed_swaps_hist = [num_failed_swaps]
    total_swaps = 0
    total_iters = 0
    while num_failed_swaps < args.max_swap_fails:
        i, k = random.sample(range(0, len(target_chunks)), k=2)
        cdiff_i = ((result_chunks[i] - target_chunks[i]) ** 2).mean()
        cdiff_k = ((result_chunks[k] - target_chunks[k]) ** 2).mean()
        cdiff = cdiff_i + cdiff_k
        ndiff_i = ((result_chunks[k] - target_chunks[i]) ** 2).mean()
        ndiff_k = ((result_chunks[i] - target_chunks[k]) ** 2).mean()
        ndiff = ndiff_i + ndiff_k
        if ndiff < cdiff:
            num_failed_swaps_hist = num_failed_swaps_hist[-args.max_swap_fails:]
            num_failed_swaps_hist.append(num_failed_swaps)
            num_failed_swaps = 0
            total_swaps += 1
            result_chunks[i], result_chunks[k] = result_chunks[k], result_chunks[i]
        else:
            num_failed_swaps += 1
        progress_bar.progress(numpy.average(num_failed_swaps_hist), 's: {}, t: {}'.format(total_swaps, total_iters))
        total_iters += 1

    progress_bar.stop()

    soundfile.write(args.out, numpy.concatenate(result_chunks), sample_rate)


if __name__ == '__main__':
    main()
