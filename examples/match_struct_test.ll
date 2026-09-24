; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Point" = type {i64, i64}
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
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"p" = alloca %"Point"*
  %"p_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p_storage" = bitcast i8* %"p_storage_raw" to %"Point"*
  store %"Point" {i64 0, i64 0}, %"Point"* %"p_storage"
  store %"Point"* %"p_storage", %"Point"** %"p"
  %"p_load" = load %"Point"*, %"Point"** %"p"
  %"x_ptr" = getelementptr %"Point", %"Point"* %"p_load", i32 0, i32 0
  store i64 0, i64* %"x_ptr"
  %"p_load.1" = load %"Point"*, %"Point"** %"p"
  %"y_ptr" = getelementptr %"Point", %"Point"* %"p_load.1", i32 0, i32 1
  store i64 0, i64* %"y_ptr"
  %"p_load.2" = load %"Point"*, %"Point"** %"p"
  br label %"match_struct_case"
match_struct_end:
  %"match_struct_res" = phi  i8* [%".12", %"match_struct_case"], [%".19", %"match_struct_case.1"], [%".21", %"match_struct_next.1"]
  %"msg" = alloca i64
  %"str_to_int_call" = call i64 @"atoi"(i8* %"match_struct_res")
  store i64 %"str_to_int_call", i64* %"msg"
  %".24" = bitcast [12 x i8]* @"str_3" to i8*
  %".25" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %"msg_load" = load i64, i64* %"msg"
  %".26" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".27", i64 %"msg_load")
  %".28" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %"p_load.3" = load %"Point"*, %"Point"** %"p"
  %"x_ptr.1" = getelementptr %"Point", %"Point"* %"p_load.3", i32 0, i32 0
  store i64 10, i64* %"x_ptr.1"
  %"p_load.4" = load %"Point"*, %"Point"** %"p"
  %"y_ptr.1" = getelementptr %"Point", %"Point"* %"p_load.4", i32 0, i32 1
  store i64 20, i64* %"y_ptr.1"
  %"p_load.5" = load %"Point"*, %"Point"** %"p"
  br label %"match_struct_case.2"
match_struct_case:
  %".12" = bitcast [7 x i8]* @"str_0" to i8*
  br label %"match_struct_end"
match_struct_next:
  br label %"match_struct_case.1"
match_struct_case.1:
  %".15" = getelementptr %"Point", %"Point"* %"p_load.2", i32 0, i32 0
  %"bind_val" = load i64, i64* %".15"
  %"val_x" = alloca i64
  store i64 %"bind_val", i64* %"val_x"
  %".17" = getelementptr %"Point", %"Point"* %"p_load.2", i32 0, i32 1
  %"bind_val.1" = load i64, i64* %".17"
  %"val_y" = alloca i64
  store i64 %"bind_val.1", i64* %"val_y"
  %".19" = bitcast [12 x i8]* @"str_1" to i8*
  br label %"match_struct_end"
match_struct_next.1:
  %".21" = bitcast [13 x i8]* @"str_2" to i8*
  br label %"match_struct_end"
match_struct_end.1:
  %"match_struct_res.1" = phi  i8* [%".32", %"match_struct_case.2"], [%".39", %"match_struct_case.3"], [%".41", %"match_struct_next.3"]
  %"msg2" = alloca i64
  %"str_to_int_call.1" = call i64 @"atoi"(i8* %"match_struct_res.1")
  store i64 %"str_to_int_call.1", i64* %"msg2"
  %".44" = bitcast [12 x i8]* @"str_11" to i8*
  %".45" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".45", i8* %".44")
  %"msg2_load" = load i64, i64* %"msg2"
  %".46" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".46")
  %".47" = bitcast [4 x i8]* @"str_14" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".47", i64 %"msg2_load")
  %".48" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".48")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
match_struct_case.2:
  %".32" = bitcast [7 x i8]* @"str_8" to i8*
  br label %"match_struct_end.1"
match_struct_next.2:
  br label %"match_struct_case.3"
match_struct_case.3:
  %".35" = getelementptr %"Point", %"Point"* %"p_load.5", i32 0, i32 0
  %"bind_val.2" = load i64, i64* %".35"
  %"val_x.1" = alloca i64
  store i64 %"bind_val.2", i64* %"val_x.1"
  %".37" = getelementptr %"Point", %"Point"* %"p_load.5", i32 0, i32 1
  %"bind_val.3" = load i64, i64* %".37"
  %"val_y.1" = alloca i64
  store i64 %"bind_val.3", i64* %"val_y.1"
  %".39" = bitcast [12 x i8]* @"str_9" to i8*
  br label %"match_struct_end.1"
match_struct_next.3:
  %".41" = bitcast [13 x i8]* @"str_10" to i8*
  br label %"match_struct_end.1"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [7 x i8] c"Origem\00"
@"str_1" = constant [12 x i8] c"Outro ponto\00"
@"str_2" = constant [13 x i8] c"Desconhecido\00"
@"str_3" = constant [12 x i8] c"Mensagem 1:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [7 x i8] c"Origem\00"
@"str_9" = constant [12 x i8] c"Outro ponto\00"
@"str_10" = constant [13 x i8] c"Desconhecido\00"
@"str_11" = constant [12 x i8] c"Mensagem 2:\00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c" \00"
@"str_14" = constant [4 x i8] c"%ld\00"
@"str_15" = constant [2 x i8] c"\0a\00"