; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Posting" = type {i64, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
@"g_index_size" = internal global i64 0
define i64 @"hash_word"(i8* %".1")
{
hash_word_entry:
  %"word" = alloca i8*
  store i8* %".1", i8** %"word"
  br label %"hash_word_body"
hash_word_body:
  %"h" = alloca i64
  store i64 0, i64* %"h"
  %"word_load" = load i8*, i8** %"word"
  %"len_str" = call i64 @"strlen"(i8* %"word_load")
  %"len" = alloca i64
  store i64 %"len_str", i64* %"len"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"len_load" = load i64, i64* %"len"
  %"icmp" = icmp slt i64 %"i_load", %"len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"h_load" = load i64, i64* %"h"
  %"mul" = mul i64 %"h_load", 31
  %"word_load.1" = load i8*, i8** %"word"
  %"i_load.1" = load i64, i64* %"i"
  %".10" = getelementptr i8, i8* %"word_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".10"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"add" = add i64 %"mul", %"idx_sext"
  store i64 %"add", i64* %"h"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"h_load.1" = load i64, i64* %"h"
  ret i64 %"h_load.1"
}

define void @"index_word"(i8* %".1", i64 %".2")
{
index_word_entry:
  %"word" = alloca i8*
  store i8* %".1", i8** %"word"
  %"doc_id" = alloca i64
  store i64 %".2", i64* %"doc_id"
  br label %"index_word_body"
index_word_body:
  %"word_load" = load i8*, i8** %"word"
  %"hash_word_call" = call i64 @"hash_word"(i8* %"word_load")
  %"h" = alloca i64
  store i64 %"hash_word_call", i64* %"h"
  %"h_load" = load i64, i64* %"h"
  %"alloc_size" = mul i64 1000, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"g_index_size_load" = load i64, i64* @"g_index_size"
  %"idx_ptr" = getelementptr i8, i8* %"alloc_call", i64 %"g_index_size_load"
  %"elem_trunc" = trunc i64 %"h_load" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"doc_id_load" = load i64, i64* %"doc_id"
  %"alloc_size.1" = mul i64 1000, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"g_index_size_load.1" = load i64, i64* @"g_index_size"
  %"add" = add i64 %"g_index_size_load.1", 1
  %"idx_ptr.1" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"elem_trunc.1" = trunc i64 %"doc_id_load" to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"g_index_size_load.2" = load i64, i64* @"g_index_size"
  %"add.1" = add i64 %"g_index_size_load.2", 2
  store i64 %"add.1", i64* @"g_index_size"
  ret void
}

define void @"search"(i8* %".1")
{
search_entry:
  %"word" = alloca i8*
  store i8* %".1", i8** %"word"
  br label %"search_body"
search_body:
  %"word_load" = load i8*, i8** %"word"
  %"hash_word_call" = call i64 @"hash_word"(i8* %"word_load")
  %"h" = alloca i64
  store i64 %"hash_word_call", i64* %"h"
  %".6" = bitcast [15 x i8]* @"str_0" to i8*
  %"word_load.1" = load i8*, i8** %"word"
  %"sconcat_len1" = call i64 @"strlen"(i8* %".6")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"word_load.1")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".6")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"word_load.1")
  %".7" = bitcast [5 x i8]* @"str_1" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".7")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".7")
  %".8" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %"sconcat_buf.1")
  %".9" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"found" = alloca i64
  store i64 0, i64* %"found"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_index_size_load" = load i64, i64* @"g_index_size"
  %"icmp" = icmp slt i64 %"i_load", %"g_index_size_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_size" = mul i64 1000, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".14" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".14"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"h_load" = load i64, i64* %"h"
  %"icmp.1" = icmp eq i64 %"idx_sext", %"h_load"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"found_load.1" = load i64, i64* %"found"
  %"icmp.2" = icmp eq i64 %"found_load.1", 0
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then:
  %"alloc_size.1" = mul i64 1000, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %".16" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"ptr_idx_load.1" = load i8, i8* %".16"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"doc_id" = alloca i64
  store i64 %"idx_sext.1", i64* %"doc_id"
  %".18" = bitcast [30 x i8]* @"str_4" to i8*
  %".19" = bitcast [3 x i8]* @"str_5" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".19", i8* %".18")
  %"doc_id_load" = load i64, i64* %"doc_id"
  %".20" = bitcast [2 x i8]* @"str_6" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [4 x i8]* @"str_7" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".21", i64 %"doc_id_load")
  %".22" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %"found_load" = load i64, i64* %"found"
  %"add.1" = add i64 %"found_load", 1
  store i64 %"add.1", i64* %"found"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add.2" = add i64 %"i_load.3", 2
  store i64 %"add.2", i64* %"i"
  br label %"while_cond"
if_then.1:
  %".29" = bitcast [34 x i8]* @"str_9" to i8*
  %".30" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %".31" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  ret void
}

define void @"index_document"(i8* %".1", i64 %".2")
{
index_document_entry:
  %"text" = alloca i8*
  store i8* %".1", i8** %"text"
  %"doc_id" = alloca i64
  store i64 %".2", i64* %"doc_id"
  br label %"index_document_body"
index_document_body:
  %".7" = bitcast [1 x i8]* @"str_12" to i8*
  %"current_word" = alloca i8*
  store i8* %".7", i8** %"current_word"
  %"text_load" = load i8*, i8** %"text"
  %"len_str" = call i64 @"strlen"(i8* %"text_load")
  %"length" = alloca i64
  store i64 %"len_str", i64* %"length"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"length_load" = load i64, i64* %"length"
  %"icmp" = icmp slt i64 %"i_load", %"length_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"text_load.1" = load i8*, i8** %"text"
  %"i_load.1" = load i64, i64* %"i"
  %".13" = getelementptr i8, i8* %"text_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".13"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp.1" = icmp eq i64 %"c_load", 32
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"current_word_load.3" = load i8*, i8** %"current_word"
  %"len_str.2" = call i64 @"strlen"(i8* %"current_word_load.3")
  %"icmp.3" = icmp sgt i64 %"len_str.2", 0
  br i1 %"icmp.3", label %"if_then.2", label %"if_else.2"
if_then:
  %"current_word_load" = load i8*, i8** %"current_word"
  %"len_str.1" = call i64 @"strlen"(i8* %"current_word_load")
  %"icmp.2" = icmp sgt i64 %"len_str.1", 0
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_else:
  %"current_word_load.2" = load i8*, i8** %"current_word"
  %"c_load.1" = load i64, i64* %"c"
  %"chr_trunc" = trunc i64 %"c_load.1" to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"current_word_load.2")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"chr_buf")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"current_word_load.2")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"chr_buf")
  store i8* %"sconcat_buf", i8** %"current_word"
  br label %"if_end"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
if_then.1:
  %"current_word_load.1" = load i8*, i8** %"current_word"
  %"doc_id_load" = load i64, i64* %"doc_id"
  call void @"index_word"(i8* %"current_word_load.1", i64 %"doc_id_load")
  %".17" = bitcast [1 x i8]* @"str_13" to i8*
  store i8* %".17", i8** %"current_word"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"if_end"
if_then.2:
  %"current_word_load.4" = load i8*, i8** %"current_word"
  %"doc_id_load.1" = load i64, i64* %"doc_id"
  call void @"index_word"(i8* %"current_word_load.4", i64 %"doc_id_load.1")
  br label %"if_end.2"
if_else.2:
  br label %"if_end.2"
if_end.2:
  ret void
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [42 x i8]* @"str_14" to i8*
  %".8" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %".10" = bitcast [38 x i8]* @"str_17" to i8*
  call void @"index_document"(i8* %".10", i64 1)
  %".11" = bitcast [40 x i8]* @"str_18" to i8*
  call void @"index_document"(i8* %".11", i64 2)
  %".12" = bitcast [23 x i8]* @"str_19" to i8*
  call void @"index_document"(i8* %".12", i64 3)
  %".13" = bitcast [43 x i8]* @"str_20" to i8*
  %".14" = bitcast [3 x i8]* @"str_21" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %"g_index_size_load" = load i64, i64* @"g_index_size"
  %"div" = sdiv i64 %"g_index_size_load", 2
  %".15" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [4 x i8]* @"str_23" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i64 %"div")
  %".17" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [42 x i8]* @"str_25" to i8*
  %".19" = bitcast [3 x i8]* @"str_26" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".19", i8* %".18")
  %".20" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [9 x i8]* @"str_28" to i8*
  call void @"search"(i8* %".21")
  %".22" = bitcast [5 x i8]* @"str_29" to i8*
  call void @"search"(i8* %".22")
  %".23" = bitcast [5 x i8]* @"str_30" to i8*
  call void @"search"(i8* %".23")
  %".24" = bitcast [5 x i8]* @"str_31" to i8*
  call void @"search"(i8* %".24")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [15 x i8] c"Buscando por '\00"
@"str_1" = constant [5 x i8] c"'...\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [30 x i8] c"  -> Encontrada no Documento:\00"
@"str_5" = constant [3 x i8] c"%s\00"
@"str_6" = constant [2 x i8] c" \00"
@"str_7" = constant [4 x i8] c"%ld\00"
@"str_8" = constant [2 x i8] c"\0a\00"
@"str_9" = constant [34 x i8] c"  -> Nenhum resultado encontrado.\00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c"\0a\00"
@"str_12" = constant [1 x i8] c"\00"
@"str_13" = constant [1 x i8] c"\00"
@"str_14" = constant [42 x i8] c"\f0\9f\8f\97\ef\b8\8f  Construindo \c3\8dndice Invertido...\00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c"\0a\00"
@"str_17" = constant [38 x i8] c"lumina is a fast programming language\00"
@"str_18" = constant [40 x i8] c"the language is compiled to native code\00"
@"str_19" = constant [23 x i8] c"fast code is good code\00"
@"str_20" = constant [43 x i8] c"Indexa\c3\a7\c3\a3o conclu\c3\adda! Total de postings:\00"
@"str_21" = constant [3 x i8] c"%s\00"
@"str_22" = constant [2 x i8] c" \00"
@"str_23" = constant [4 x i8] c"%ld\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [42 x i8] c"-----------------------------------------\00"
@"str_26" = constant [3 x i8] c"%s\00"
@"str_27" = constant [2 x i8] c"\0a\00"
@"str_28" = constant [9 x i8] c"language\00"
@"str_29" = constant [5 x i8] c"fast\00"
@"str_30" = constant [5 x i8] c"code\00"
@"str_31" = constant [5 x i8] c"rust\00"