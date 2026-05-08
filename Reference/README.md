# Schoenflies

/ˈʃøːnfliːs/

Determine and visualise molecular symmetry.

## Releases

[Click here to download pre-built Schoenflies binaries.](https://gitlab.com/lkkmpn/schoenflies/-/releases)

## Dependencies (Debian 11)

```
sudo apt install build-essential cmake qtbase5-dev qtbase5-dev-tools libboost-all-dev libeigen3-dev libfreetype-dev libglm-dev nlohmann-json3-dev
```

## Compilation (Debian 11)

```
$ cd build
$ cmake ..
$ make -j5
```

## Testing

After compilation, run `build/test/schoenflies_test`. Ensure that the working
directory is a descendant of the project's root directory (or the project's
root directory itself) so that required test files can be found.

## License

This project is licensed under [the GNU GPL v3 license.](LICENSE.md)

## Funding

Development of this project is partially funded by
[the BOOST! program of Eindhoven University of Technology.](https://boost.tue.nl)
