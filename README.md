# Wikiracer

This is my attempt at a CLI wikiracer in python.

## Overview

In order to quickly find an intersection between the source and destination, I'm using a
bidirectional BFS, which is significantly more efficient than a standard BFS for this. The core
component of this solution is the BFSBranch class, which represents a single direction of the BFS.

In the main file, I create an event loop to allow me to send off many concurrent API requests. I
alternate between requesting pages from the source and destination branches. Instead of requesting
links from all pages in a branch's queue, I instead request the first n pages, where n is the
number of worker threads I have. This gives us a huge speedup by giving us a basic round robin
scheduler between the two branches, instead of completing one branch's queue before the other. When
I initially tried this, I was finishing each branch's queue before moving on to the other, but that
caused issues where one branch could be much larger than the other, causing the algorithm to get
stuck trying to finish that side of the search before it could continue searching from the other
side. After each time I request link data, I compare the caches of the two branches to see if an
intersection exists. If it does, I know that the path from source to destination can be completed.
The cache data in each branch allows me to reconstruct the path from the initial page to the
intersection page, so I can generate the entire path trivially.

## Instructions

Python >= 3.4

`pip install -r requirements.txt` to install dependencies.

`./wikiracer.py "Source Page" "Target Page"` to race. You can modify the number of concurrent
requests with the `--workers` flag.

`./wikiracer.py --help` to see usage.

## Strategies I tried

I initially wrote a standard BFS to traverse the tree. While this was able to eventually find a
path, it was not very efficient (Segment->The game in 4:30). I was able to significantly speed up
my code by batching API requests to get links for 50 pages at a time and making the BFS
bidirectional (Segment->The game in 0:03). However, since I was batching the API requests, I wasn't
able to track parent/child relationships for encountered links, since the links could be from any of
the provided parents. I had to revert to requesting a single page's information at a time, which
came with a pretty decent slowdown (Segment->The game in 0:13). I had never really worked with
concurrency in Python before, so I had to wrap my head around the new (since 3.4) asyncio library,
as well as the requests_futures module. After a lot of effort, I was able to make HTTP requests in
parallel, while doing some parsing as a callback provided to requests_futures.session.get().
Once the entire batch of requests had completed, I processed the new page data and added the
necessary pages to the queue and started the whole process again. This brought me to my fastest
time, and was in a state where I was fairly confident I couldn't speed it up much more
(Segment->The game in 0:05).

## How long I spent (roughly)

- Basic BFS and API wrapper - 1 hour
- Batching requests - 1 hour
- Caching pages to calculate path - 2 hours
- Initial hacky single-file async solution - 4 hours
- Design of BFSBranch class with new async architecture - 1 hour
- Refactoring to create BFSBranch class - 1 hour
- Cleanup - 1 hour
- Documentation/tests/README - 2 hours
