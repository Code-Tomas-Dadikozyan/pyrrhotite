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

#include <string>
#include <vector>
#include <boost/test/unit_test.hpp>
#include "../src/library/library_package.h"
#include "../src/symmetry/point_groups/point_group_label.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(library_package);

BOOST_AUTO_TEST_CASE(library_package) {
    std::string filename = resolve_path("test/files/test_library.json");
    LibraryPackage package(filename);
    BOOST_TEST(package.get_size() == 4);
}

BOOST_AUTO_TEST_CASE(library_items) {
    std::vector<std::string> names = {
        "Benzene",
        "Cubane",
        "Methane",
        "Water"
    };
    std::vector<std::vector<std::string>> path_parts = {
        {"test", "files", "benzene"},
        {"test", "files", "cubane"},
        {"test", "files", "methane"},
        {"test", "files", "water"}
    };
    std::vector<std::string> chemical_formulas = {
        "C<sub>6</sub>H<sub>6</sub>",
        "C<sub>8</sub>H<sub>8</sub>",
        "CH<sub>4</sub>",
        "H<sub>2</sub>O"
    };
    std::vector<PointGroupLabel> point_group_labels = {
        PointGroupLabel(PointGroupLabel::Class::Dh, 6),
        PointGroupLabel(PointGroupLabel::Class::Oh),
        PointGroupLabel(PointGroupLabel::Class::Td),
        PointGroupLabel(PointGroupLabel::Class::Cv, 2)
    };

    std::string filename = resolve_path("test/files/test_library.json");
    LibraryPackage package(filename);

    for (unsigned int i = 0; i < 4; ++i) {
        auto item = package.get_item(i);
        BOOST_TEST(item.get_name() == names[i]);
        for (unsigned int j = 0; j < path_parts[i].size(); ++j) {
            BOOST_TEST(item.get_path().find(path_parts[i][j]) != std::string::npos);
        }
        BOOST_TEST(item.get_chemical_formula() == chemical_formulas[i]);
        BOOST_TEST(item.get_point_group_label().matches(point_group_labels[i]));
        BOOST_TEST(item.get_item_practice_config().contains("flowchart"));
        BOOST_TEST(item.get_item_practice_config()["flowchart"].contains("enabled"));
        BOOST_TEST(item.get_item_practice_config()["flowchart"]["enabled"] == true);
    }
}

BOOST_AUTO_TEST_SUITE_END();
