; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"English" = type {i64}
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
define i8* @"English_name"(%"English"* %".1")
{
English_name_entry:
  %"self" = alloca %"English"*
  store %"English"* %".1", %"English"** %"self"
  br label %"English_name_body"
English_name_body:
  %".5" = bitcast [7 x i8]* @"str_0" to i8*
  ret i8* %".5"
}

define void @"English_greet"(%"English"* %".1")
{
English_greet_entry:
  %"self" = alloca %"English"*
  store %"English"* %".1", %"English"** %"self"
  br label %"English_greet_body"
English_greet_body:
  %"self_load" = load %"English"*, %"English"** %"self"
  %"name_alias_call" = call i8* @"English_name"(%"English"* %"self_load")
  %"n" = alloca i8*
  store i8* %"name_alias_call", i8** %"n"
  %".6" = bitcast [11 x i8]* @"str_1" to i8*
  %".7" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".7", i8* %".6")
  %"n_load" = load i8*, i8** %"n"
  %".8" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".8")
  %".9" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".9", i8* %"n_load")
  %".10" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".10")
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
  %"e" = alloca %"English"*
  %"e_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"e_storage" = bitcast i8* %"e_storage_raw" to %"English"*
  store %"English" {i64 0}, %"English"* %"e_storage"
  store %"English"* %"e_storage", %"English"** %"e"
  %"e_load" = load %"English"*, %"English"** %"e"
  %"dummy_ptr" = getelementptr %"English", %"English"* %"e_load", i32 0, i32 0
  store i64 0, i64* %"dummy_ptr"
  %"e_load.1" = load %"English"*, %"English"** %"e"
  call void @"English_greet"(%"English"* %"e_load.1")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [7 x i8] c"Lumina\00"
@"str_1" = constant [11 x i8] c"Hello from\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c" \00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"