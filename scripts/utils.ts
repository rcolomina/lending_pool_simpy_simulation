import { join } from 'path';
import { readFileSync, writeFileSync } from 'fs';

// ✅ write to file SYNCHRONOUSLY
export function syncWriteFile(filename: string, data: any) {
  /**
   * flags:
   *  - w = Open file for reading and writing. File is created if not exists
   *  - a+ = Open file for reading and appending. The file is created if not exists
   */
  writeFileSync(join(__dirname, filename), data, {
    flag: 'w',
  });

  const contents = readFileSync(join(__dirname, filename), 'utf-8');
  console.log(contents); // 👉️ "One Two Three Four"

  return contents;
}
