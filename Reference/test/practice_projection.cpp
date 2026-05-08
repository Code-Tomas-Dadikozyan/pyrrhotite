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

#include <memory>
#include <string>
#include <vector>
#include <boost/test/unit_test.hpp>
#include "../src/library/library.h"
#include "../src/library/library_item.h"
#include "../src/practice/practice_projection.h"
#include "../src/practice/practice_structure.h"
#include "../src/symmetry/symmetry.h"
#include "../src/basis_set.h"
#include "../src/structure.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(practice_projection);

BOOST_AUTO_TEST_CASE(benzene) {
    std::string file = resolve_path("test/files/test_library_practice.json");
    Library library(false);
    library.add_items_from_package(file);
    LibraryItem item = library.get_items()[0];

    auto struc = std::make_shared<Structure>(item.get_path());
    struc->set_library_item(std::make_shared<LibraryItem>(item));
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry, false);
    PracticeProjection projection(practice_structure);

    BOOST_TEST(practice_structure->get_basis_set()->get_element().symbol == "C");
    BOOST_TEST(practice_structure->get_basis_set()->get_orbital_label().get_principal() == 2);
    BOOST_TEST(practice_structure->get_basis_set()->get_orbital_label().get_azimuthal() == 1);
    BOOST_TEST(practice_structure->get_basis_set()->get_orbital_label().get_magnetic() == 0);

    BOOST_TEST(practice_structure->get_base_atom() == 0);

    auto calculated_coefficients = projection.get_correct_coefficients();
    std::vector<std::vector<double>> correct_coefficients = {
        {0, 1, 0, 0, 0, 1},
        {0, 0, 1, 0, 1, 0},
        {0, 0, 0, 1, 0, 0},
        {-1, 0, -1, 0, -1, 0},
        {0, -1, 0, -1, 0, -1},
        {0, 0, 0, -1, 0, 0},
        {0, -1, 0, 0, 0, -1},
        {0, 0, -1, 0, -1, 0},
        {-1, 0, 0, 0, 0, 0},
        {1, 0, 1, 0, 1, 0},
        {0, 1, 0, 1, 0, 1}
    };

    for (unsigned int i = 0; i < correct_coefficients.size(); ++i) {
        for (unsigned int j = 0; j < correct_coefficients[i].size(); ++j) {
            BOOST_TEST(calculated_coefficients[i].second[j] == correct_coefficients[i][j], boost::test_tools::tolerance(1e-7));
        }
    }
}

BOOST_AUTO_TEST_SUITE_END();
