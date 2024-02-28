import re

section_pattern = re.compile(r'\s{3,}SECTION M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})')
chapter_pattern = re.compile(r'\n\s+Chapter \d+\s+\n')
subchapter_pattern = re.compile(r'\n\s+\d{2}\.\d{2}\s+')


def split_into_sections_and_chapters(input_file_path):
    section_counter = 0  # Counter for the section files
    current_section_content = []  # Holds the content of the current parsing section

    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if section_pattern.match(line):
                if current_section_content:
                    section_counter += 1
                    split_section_into_chapters(section_counter, current_section_content)
                    current_section_content = []
            current_section_content.append(line)

        if current_section_content:
            section_counter += 1
            split_section_into_chapters(section_counter, current_section_content)


def split_section_into_chapters(section_counter, section_content):
    chapters = chapter_pattern.split(''.join(section_content))
    chapter_matches = chapter_pattern.findall(''.join(section_content))

    if chapters and len(chapters) > 1:  # Check if multiple chapters were found within the section
        for idx, chapter in enumerate(chapters):
            if idx > 0:  # Skip the first split as it's before the first chapter
                chapter_title = chapter_matches[idx - 1].strip()
                chapter_number = idx
                write_chapter_to_file(section_counter, chapter_number, chapter_title, chapter)
                split_chapter_into_subchapters(section_counter, chapter_number, chapter_title, chapter)
    else:  # If no chapters are found, treat the whole section as a single chapter
        split_chapter_into_subchapters(section_counter, 1, 'Chapter 1', ''.join(section_content))


def split_chapter_into_subchapters(section_number, chapter_number, chapter_title, chapter_content):
    subchapters = subchapter_pattern.split(chapter_content)
    subchapter_matches = subchapter_pattern.findall(chapter_content)

    if subchapters and len(subchapters) > 1:
        for idx, subchapter in enumerate(subchapters):
            if idx > 0:
                subchapter_title = subchapter_matches[idx - 1].strip()
                subchapter_number = idx
                write_subchapter_to_file(section_number, chapter_number, subchapter_number, subchapter_title,
                                         subchapter)
    else:
        write_subchapter_to_file(section_number, chapter_number, 1, chapter_title, chapter_content)


def write_subchapter_to_file(section_number, chapter_number, subchapter_number, subchapter_title, subchapter_content):
    subchapter_file_name = f'Section_{section_number}_Chapter_{chapter_number}_Subchapter_{subchapter_number}.txt'
    with open(subchapter_file_name, 'w', encoding='utf-8') as subchapter_file:
        subchapter_file.write(subchapter_title + "\n" + subchapter_content)
    print(
        f'Subchapter {subchapter_number} of Chapter {chapter_number} of Section {section_number} has been saved to {subchapter_file_name}')


def write_chapter_to_file(section_number, chapter_number, chapter_title, chapter_content):
    # Define the chapter's file name with both section and chapter numbers
    subchapter_start_match = subchapter_pattern.search(chapter_content)
    if subchapter_start_match:
        chapter_content = chapter_content[:subchapter_start_match.start()]
    chapter_file_name = f'Section_{section_number}_Chapter_{chapter_number}.txt'
    with open(chapter_file_name, 'w', encoding='utf-8') as chapter_file:
        chapter_file.write(chapter_title + "\n" + chapter_content)  # Write the title and the content to the file
    print(f'Chapter {chapter_number} of Section {section_number} has been saved to {chapter_file_name}')


if __name__ == "__main__":
    # Replace 'your_input_file.txt' with the path to your text file
    input_file_path = 'stcced.txt'
    split_into_sections_and_chapters(input_file_path)
