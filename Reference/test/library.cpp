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

#include <boost/test/unit_test.hpp>
#include "../src/library/library.h"
#include "../src/symmetry/point_groups/point_group_label.h"

BOOST_AUTO_TEST_SUITE(library);

BOOST_AUTO_TEST_CASE(library) {
    Library library;  // built-in library
    BOOST_TEST(library.get_items().size() > 0);
}

BOOST_AUTO_TEST_CASE(library_item) {
    Library library;  // built-in library

    // test a single item
    bool found = false;
    for (auto item : library.get_items()) {
        if (item.get_path()[0] == ':' &&
            item.get_path().find("assets") != std::string::npos &&
            item.get_path().find("structures") != std::string::npos &&
            item.get_path().find("benzene.xyz") != std::string::npos) {  // prevent directory separator issues
            found = true;
            BOOST_TEST(item.get_name() == "Benzene");
            BOOST_TEST(item.get_chemical_formula() == "C<sub>6</sub>H<sub>6</sub>");
            PointGroupLabel correct(PointGroupLabel::Class::Dh, 6);
            BOOST_TEST(item.get_point_group_label().matches(correct));
            BOOST_TEST(item.get_item_practice_config().contains("flowchart"));
            BOOST_TEST(item.get_item_practice_config()["flowchart"].contains("enabled"));
            BOOST_TEST(item.get_item_practice_config()["flowchart"]["enabled"] == true);
        }
    }

    BOOST_TEST(found);
}

BOOST_AUTO_TEST_SUITE_END();
