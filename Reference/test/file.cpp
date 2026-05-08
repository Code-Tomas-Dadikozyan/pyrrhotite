/**
 * Schoenflies
 * Copyright (c) 2022 Luuk Kempen
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include <ios>
#include <stdexcept>
#include <string>
#include <QFile>
#include <boost/test/unit_test.hpp>
#include "../src/file.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(file);

BOOST_AUTO_TEST_CASE(load_file_disk) {
    std::string filename = resolve_path("test/files/water.xyz");
    File file(filename);

    BOOST_TEST(file.get_source() == File::Source::Disk);

    file.get_stream().seekg(0, std::ios::end);
    int size = file.get_stream().tellg();

    BOOST_TEST(size == 125);
}

BOOST_AUTO_TEST_CASE(load_file_qt) {
    std::string filename = ":/assets/structures/water.xyz";
    File file(":/assets/structures/water.xyz");

    BOOST_TEST(file.get_source() == File::Source::QtResource);

    file.get_stream().seekg(0, std::ios::end);
    int size = file.get_stream().tellg();

    BOOST_TEST(size == 107);
}

BOOST_AUTO_TEST_CASE(load_nonexistant_file_disk) {
    std::string filename = "qwertyuiop.xyz";
    BOOST_CHECK_THROW(File file(filename), std::runtime_error);
}

BOOST_AUTO_TEST_CASE(load_nonexistant_file_qt) {
    std::string filename = ":/assets/qwertyuiop.xyz";
    BOOST_CHECK_THROW(File file(filename), std::runtime_error);
}

BOOST_AUTO_TEST_SUITE_END();
