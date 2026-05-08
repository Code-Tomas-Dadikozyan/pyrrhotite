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

#ifndef FILE_H
#define FILE_H

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <QByteArray>
#include <QFile>
#include <QIODevice>
#include <QString>

class File {
public:
    enum Source {
        Disk,
        QtResource
    };

private:
    std::stringstream stream;
    Source source;

public:
    /**
     * @brief Construct a new File object
     *
     * @param path name of the file
     */
    File(const std::string path);

    /**
     * @brief Get the stream object
     *
     * @return std::stringstream&
     */
    std::stringstream& get_stream();

    /**
     * @brief Get the source of the file
     *
     * @return Source
     */
    Source get_source();

private:
    /**
     * @brief Read file from disk
     *
     * @param path name of the file
     */
    void read_from_disk(const std::string& path);

    /**
     * @brief Read file from the Qt resource system
     *
     * @param path name of the file
     */
    void read_qt_resource(const std::string& path);
};

#endif  // FILE_H
