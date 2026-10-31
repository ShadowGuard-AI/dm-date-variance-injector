![Banner](banner.png)

# dm-date-variance-injector
Introduces a random variance within a specified range to date values, preserving the temporal relationships while obscuring exact dates. Useful for masking date of birth or service initiation dates. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowStrikeHQ/dm-date-variance-injector`

## Usage
`./dm-date-variance-injector [params]`

## Parameters
- `-h`: Show help message and exit
- `-r`: The range of days to vary the date by. A positive value draws only into the future, from 1 to the range. A negative value draws only into the past, from the range to -1.
- `-m`: No description provided
- `-f`: No description provided
- `-s`: Optional seed for the shared offset draw, so a run can be reproduced.

One run can take one or more dates. All dates in a single run share one drawn offset, so their order is preserved: a later date in the input stays later in the output. Dates masked in separate runs do not share an offset. With --seed, the shared offset is the seeded draw, so the same seed and range reproduce the same shift for the whole set.

## License
Copyright (c) ShadowStrikeHQ
