def list_elements_in_common(list1, list2):
    #return the index of the common element
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] == "" or list2[j] == "":
                continue
            if list1[i] == list2[j]:
                return i, j
    return -1, -1

def stringify_list(list):
    string = ""
    for i in list:
        string += i
    return string

def tag_as_deleted(string):
    return f"<deleted> {stringify_list(string)} </deleted> "

def tag_as_added(string):
    return f"<added> {stringify_list(string)} </added> "

def tag_as_modified_from(string):
    return f"<modified_from> {stringify_list(string)} </modified_from> "

def tag_as_modified_to(string):
    return f"<modified_to> {stringify_list(string)} </modified_to> "

def tag_as_unchanged(string):
    return f"{stringify_list(string)} "

def fix_img_tag(wordList):
    tagStart = -1
    tagEnd = -1
    insideTag = False
    resultList = []
    skipOnce = False
    for i in range(len(wordList)):
        if skipOnce:
            skipOnce = False
            continue
        elif wordList[i] == "<" and wordList[i+1] == "img":
            tagStart = i
            insideTag = True
        elif wordList[i] == "/" and wordList[i+1] == ">" and insideTag:
            tagEnd = i
            combinedString = ""
            for j in range(tagStart, tagStart+2):
                combinedString += wordList[j]
            combinedString += " "
            for j in range(tagStart+2, tagEnd+2):
                combinedString += wordList[j]
            resultList.append(combinedString)
            tagStart = -1
            tagEnd = -1
            insideTag = False
            skipOnce = True
        else:
            if not insideTag:
                resultList.append(wordList[i])
    return resultList

def split_string(string):
    words = []
    current_word = ""
    for c in string:
        if isPunctuation(c): # 문장부호는 공백으로 분리
            # current_word += c
            words.append(current_word) # 단어 추가
            words.append(c) # 문장부호 추가
            current_word = ""
        elif isNonSpaceWhitespace(c):
            words.append(current_word) # 단어 추가
            words.append(c) # 문장부호 추가 (줄바꿈 기호 보존해야함)
            current_word = ""
        elif c == " ":
            if current_word == "":
                continue
            words.append(current_word)
            current_word = ""
        else:
            current_word += c
    
    if current_word != "":
        words.append(current_word)
        current_word = ""

    for word in words:
        if word == "":
            words.remove(word)

    words = fix_img_tag(words)
    # print(words)

    return words

def isPunctuation(c):
    if c in ".,!?": return True
    if c in "[]():": return True
    if c in ";'": return True
    if c in "\"`": return True
    return False
    
def isNonSpaceWhitespace(c):
    return c == "\n" or c == "\t"

def diff_strings(old_string, new_string):

    resultString = ""

    old_words = split_string(old_string)
    new_words = split_string(new_string)

    old_words.append("")
    new_words.append("")

    # 초기 설정
    i_old = 0
    i_new = 0
    old_temp = []
    new_temp = []

    # 리스트가 끝나기 전까지 루프
    while i_old < len(old_words) and i_new < len(new_words):
        # print(f"old: {old_words[i_old]} => new: {new_words[i_new]}")
        # 현재 가리킨 단어가 같은 단어인 경우
        if old_words[i_old] == new_words[i_new]:
            # 두 리스트 모두 끝에 도달한 경우 조기종료
            if(old_words[i_old] == ""):
                i_old = len(old_words)
                i_new = len(new_words)
                break

            resultString += tag_as_unchanged(old_words[i_old])
            # print(" -> unchanged")
            
            # 인디케이터 증가
            i_old += 1
            i_new += 1
            saved_i_new = i_new
            saved_i_old = i_old
            
            old_temp = []
            new_temp = []
        else:
            # 인디케이터 단어가 다른데 둘 중 하나가 끝에 도달한 경우
            if(old_words[i_old] == "" or new_words[i_new] == ""):
                # 마지막 단어를 temp에 추가함
                if(old_words[i_old] == ""):
                    new_temp.append(new_words[i_new])
                elif(new_words[i_new] == ""):
                    old_temp.append(old_words[i_old])
                break

            # 완료된 부분까지 저장
            saved_i_old = i_old
            saved_i_new = i_new

            # 다른 단어를 temp에 추가
            old_temp.append(old_words[i_old])
            new_temp.append(new_words[i_new])

            # 인디케이터 증가
            if(i_old < len(old_words)):
                i_old += 1
            if(i_new < len(new_words)): 
                i_new += 1

            # 공통단어가 나오거나 끝날 때까지 인디케이터 증가
            if(i_old >= len(old_words) and i_new >= len(new_words)):
                break
            while (i_old < len(old_words) and i_new < len(new_words) and
                old_words[i_old] not in new_temp and new_words[i_new] not in old_temp):
                
                if(i_old == len(old_words)-1 and i_new == len(new_words)-1):
                    break
                # 인디케이터 증가
                if(i_old < len(old_words)-1):
                    old_temp.append(old_words[i_old])
                    i_old += 1
                if(i_new < len(new_words)-1):
                    new_temp.append(new_words[i_new])
                    i_new += 1

            if (i_old < len(old_words) and i_new < len(new_words)):
                old_temp.append(old_words[i_old])
                new_temp.append(new_words[i_new])

                # 공통단어 : added
                if(new_words[i_new] == old_words[saved_i_old]):
                    new_temp.pop()
                    resultString += tag_as_added(' '.join(new_temp))
                    # print(" -> added (type A)")

                    i_old = saved_i_old
                    i_new = i_new
                    old_temp = []
                    new_temp = []
                    continue

                # 공통단어 : deleted
                if (old_words[i_old] == new_words[saved_i_new]):
                    
                    old_temp.pop()

                    resultString += tag_as_deleted({' '.join(old_temp)})
                    # print(" -> deleted (type A)")

                    i_old = i_old
                    i_new = saved_i_new

                    old_temp = []
                    new_temp = []
                    continue
                
                elements_in_common = list_elements_in_common(old_temp, new_temp)
                # 공통단어 : modified
                if (elements_in_common != (-1, -1)):
                    i_old, i_new = elements_in_common

                    # 공통단어 이후 삭제
                    old_temp = old_temp[:i_old]
                    new_temp = new_temp[:i_new]
                    
                    resultString += tag_as_modified_from(' '.join(old_temp))
                    resultString += tag_as_modified_to(' '.join(new_temp))
                    # print(" -> modified (type A)")

                    i_old = saved_i_old + i_old
                    i_new = saved_i_new + i_new

                    old_temp = []
                    new_temp = []
                    continue

    # old/new 리스트에 남은 단어 처리
    final_delete = ' '.join(old_words[saved_i_old:]).strip()
    final_add = ' '.join(new_words[saved_i_new:]).strip()

    if (final_delete != "" and final_add != ""):
        resultString += tag_as_modified_from(final_delete)
        resultString += tag_as_modified_to(final_add)
        # print(" -> modified (type B)")
        
    else:
        if(final_delete != ""):
            resultString += tag_as_deleted(final_delete)
            # print(" -> deleted (type B)")
        if(final_add != ""):
            resultString += tag_as_added(final_add)
            # print(" -> added (type B)")

    # print()

    # 문장 부호 앞에 공백 있으면 제거. 해당하는 문장부호는 .,!?
    resultString = resultString.replace(" .", ".").replace(" ,", ",").replace(" !", "!").replace(" ?", "?")

    return resultString