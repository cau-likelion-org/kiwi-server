def list_elements_in_common(list1, list2):
    #return the index of the common element
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] == "" or list2[j] == "":
                continue
            if list1[i] == list2[j]:
                return i, j
    return -1, -1

def tag_as_deleted(string):
    return f"<deleted> {string} </deleted> "

def tag_as_added(string):
    return f"<added> {string} </added> "

def tag_as_modified_from(string):
    return f"<modified_from> {string} </modified_from> "

def tag_as_modified_to(string):
    return f"<modified_to> {string} </modified_to> "

def tag_as_unchanged(string):
    return f"{string} "


def diff_strings(old_string, new_string):

    resultString = ""

    old_words = old_string.split()
    new_words = new_string.split()

    old_words.append("")
    new_words.append("")

    # 초기 설정
    i_old = 0
    i_new = 0
    old_temp = []
    new_temp = []

    # 리스트가 끝나기 전까지 루프
    while i_old < len(old_words) and i_new < len(new_words):
        # 현재 가리킨 단어가 같은 단어인 경우
        if old_words[i_old] == new_words[i_new]:
            # 두 리스트 모두 끝에 도달한 경우 조기종료
            if(old_words[i_old] == ""):
                i_old = len(old_words)
                i_new = len(new_words)
                break

            resultString += tag_as_unchanged(old_words[i_old])
            
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

                    resultString += tag_as_added(' '.join(new_temp))
                    
                    i_old = saved_i_old
                    i_new = i_new
                    old_temp = []
                    new_temp = []
                    continue

                # 공통단어 : deleted
                if (old_words[i_old] == new_words[saved_i_new]):
                    
                    resultString += tag_as_deleted({' '.join(old_temp)})
                    
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
        
    else:
        if(final_delete != ""):
            resultString += tag_as_deleted(final_delete)
        if(final_add != ""):
            resultString += tag_as_added(final_add)

    return resultString