#include "FS.h"
#include <LITTLEFS.h>

#define FORMAT_LITTLEFS_IF_FAILED true

void listDir(fs::FS &fs, const char * dirname, uint8_t levels);
void createDir(fs::FS &fs, const char * path);
void removeDir(fs::FS &fs, const char * path);
void readFile(fs::FS &fs, const char * path);
void writeFile(fs::FS &fs, const char * path, const char * message);
void appendFile(fs::FS &fs, const char * path, const char * message);
void renameFile(fs::FS &fs, const char * path1, const char * path2);
void deleteFile(fs::FS &fs, const char * path);

// SPIFFS-like write and delete file, better use #define CONFIG_LITTLEFS_SPIFFS_COMPAT 1
void writeFile2(fs::FS &fs, const char * path, const char * message);
void deleteFile2(fs::FS &fs, const char * path);
void testFileIO(fs::FS &fs, const char * path);