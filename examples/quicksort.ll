; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
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
define i64 @"partition"(i64* %".1", i64 %".2", i64 %".3")
{
partition_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"low" = alloca i64
  store i64 %".2", i64* %"low"
  %"high" = alloca i64
  store i64 %".3", i64* %"high"
  br label %"partition_body"
partition_body:
  %"arr_load" = load i64*, i64** %"arr"
  %"high_load" = load i64, i64* %"high"
  %".9" = getelementptr i64, i64* %"arr_load", i64 %"high_load"
  %"ptr_idx_load" = load i64, i64* %".9"
  %"pivot" = alloca i64
  store i64 %"ptr_idx_load", i64* %"pivot"
  %"low_load" = load i64, i64* %"low"
  %"sub" = sub i64 %"low_load", 1
  %"i" = alloca i64
  store i64 %"sub", i64* %"i"
  %"low_load.1" = load i64, i64* %"low"
  %"high_load.1" = load i64, i64* %"high"
  %"j" = alloca i64
  store i64 %"low_load.1", i64* %"j"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"j"
  %"for_cond.1" = icmp slt i64 %"for_curr", %"high_load.1"
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"arr_load.1" = load i64*, i64** %"arr"
  %"j_load" = load i64, i64* %"j"
  %".15" = getelementptr i64, i64* %"arr_load.1", i64 %"j_load"
  %"ptr_idx_load.1" = load i64, i64* %".15"
  %"pivot_load" = load i64, i64* %"pivot"
  %"icmp" = icmp sle i64 %"ptr_idx_load.1", %"pivot_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
for_inc:
  %"for_curr_inc" = load i64, i64* %"j"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"j"
  br label %"for_cond"
for_end:
  %"arr_load.6" = load i64*, i64** %"arr"
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 1
  %".28" = getelementptr i64, i64* %"arr_load.6", i64 %"add.1"
  %"ptr_idx_load.4" = load i64, i64* %".28"
  %"temp2" = alloca i64
  store i64 %"ptr_idx_load.4", i64* %"temp2"
  %"arr_load.7" = load i64*, i64** %"arr"
  %"high_load.2" = load i64, i64* %"high"
  %".30" = getelementptr i64, i64* %"arr_load.7", i64 %"high_load.2"
  %"ptr_idx_load.5" = load i64, i64* %".30"
  %"arr_load.8" = load i64*, i64** %"arr"
  %"i_load.4" = load i64, i64* %"i"
  %"add.2" = add i64 %"i_load.4", 1
  %"idx_ptr.2" = getelementptr i64, i64* %"arr_load.8", i64 %"add.2"
  store i64 %"ptr_idx_load.5", i64* %"idx_ptr.2"
  %"temp2_load" = load i64, i64* %"temp2"
  %"arr_load.9" = load i64*, i64** %"arr"
  %"high_load.3" = load i64, i64* %"high"
  %"idx_ptr.3" = getelementptr i64, i64* %"arr_load.9", i64 %"high_load.3"
  store i64 %"temp2_load", i64* %"idx_ptr.3"
  %"i_load.5" = load i64, i64* %"i"
  %"add.3" = add i64 %"i_load.5", 1
  ret i64 %"add.3"
if_then:
  %"i_load" = load i64, i64* %"i"
  %"add" = add i64 %"i_load", 1
  store i64 %"add", i64* %"i"
  %"arr_load.2" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".18" = getelementptr i64, i64* %"arr_load.2", i64 %"i_load.1"
  %"ptr_idx_load.2" = load i64, i64* %".18"
  %"temp" = alloca i64
  store i64 %"ptr_idx_load.2", i64* %"temp"
  %"arr_load.3" = load i64*, i64** %"arr"
  %"j_load.1" = load i64, i64* %"j"
  %".20" = getelementptr i64, i64* %"arr_load.3", i64 %"j_load.1"
  %"ptr_idx_load.3" = load i64, i64* %".20"
  %"arr_load.4" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load.4", i64 %"i_load.2"
  store i64 %"ptr_idx_load.3", i64* %"idx_ptr"
  %"temp_load" = load i64, i64* %"temp"
  %"arr_load.5" = load i64*, i64** %"arr"
  %"j_load.2" = load i64, i64* %"j"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.5", i64 %"j_load.2"
  store i64 %"temp_load", i64* %"idx_ptr.1"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  br label %"for_inc"
}

define void @"quicksort"(i64* %".1", i64 %".2", i64 %".3")
{
quicksort_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"low" = alloca i64
  store i64 %".2", i64* %"low"
  %"high" = alloca i64
  store i64 %".3", i64* %"high"
  br label %"quicksort_body"
quicksort_body:
  %"low_load" = load i64, i64* %"low"
  %"high_load" = load i64, i64* %"high"
  %"icmp" = icmp slt i64 %"low_load", %"high_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"arr_load" = load i64*, i64** %"arr"
  %"low_load.1" = load i64, i64* %"low"
  %"high_load.1" = load i64, i64* %"high"
  %"partition_call" = call i64 @"partition"(i64* %"arr_load", i64 %"low_load.1", i64 %"high_load.1")
  %"pi" = alloca i64
  store i64 %"partition_call", i64* %"pi"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"low_load.2" = load i64, i64* %"low"
  %"pi_load" = load i64, i64* %"pi"
  %"sub" = sub i64 %"pi_load", 1
  call void @"quicksort"(i64* %"arr_load.1", i64 %"low_load.2", i64 %"sub")
  %"arr_load.2" = load i64*, i64** %"arr"
  %"pi_load.1" = load i64, i64* %"pi"
  %"add" = add i64 %"pi_load.1", 1
  %"high_load.2" = load i64, i64* %"high"
  call void @"quicksort"(i64* %"arr_load.2", i64 %"add", i64 %"high_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
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
  %"alloc_size" = mul i64 10, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"arr" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"arr"
  %"arr_load" = load i64*, i64** %"arr"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 0
  store i64 9, i64* %"idx_ptr"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.1", i64 1
  store i64 7, i64* %"idx_ptr.1"
  %"arr_load.2" = load i64*, i64** %"arr"
  %"idx_ptr.2" = getelementptr i64, i64* %"arr_load.2", i64 2
  store i64 5, i64* %"idx_ptr.2"
  %"arr_load.3" = load i64*, i64** %"arr"
  %"idx_ptr.3" = getelementptr i64, i64* %"arr_load.3", i64 3
  store i64 11, i64* %"idx_ptr.3"
  %"arr_load.4" = load i64*, i64** %"arr"
  %"idx_ptr.4" = getelementptr i64, i64* %"arr_load.4", i64 4
  store i64 12, i64* %"idx_ptr.4"
  %"arr_load.5" = load i64*, i64** %"arr"
  %"idx_ptr.5" = getelementptr i64, i64* %"arr_load.5", i64 5
  store i64 2, i64* %"idx_ptr.5"
  %"arr_load.6" = load i64*, i64** %"arr"
  %"idx_ptr.6" = getelementptr i64, i64* %"arr_load.6", i64 6
  store i64 14, i64* %"idx_ptr.6"
  %"arr_load.7" = load i64*, i64** %"arr"
  %"idx_ptr.7" = getelementptr i64, i64* %"arr_load.7", i64 7
  store i64 3, i64* %"idx_ptr.7"
  %"arr_load.8" = load i64*, i64** %"arr"
  %"idx_ptr.8" = getelementptr i64, i64* %"arr_load.8", i64 8
  store i64 10, i64* %"idx_ptr.8"
  %"arr_load.9" = load i64*, i64** %"arr"
  %"idx_ptr.9" = getelementptr i64, i64* %"arr_load.9", i64 9
  store i64 6, i64* %"idx_ptr.9"
  %".18" = bitcast [16 x i8]* @"str_0" to i8*
  %".19" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".19", i8* %".18")
  %".20" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", 10
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"arr_load.10" = load i64*, i64** %"arr"
  %"i_load" = load i64, i64* %"i"
  %".24" = getelementptr i64, i64* %"arr_load.10", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".24"
  %".25" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"ptr_idx_load")
  %".26" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".26")
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"arr_load.11" = load i64*, i64** %"arr"
  call void @"quicksort"(i64* %"arr_load.11", i64 0, i64 9)
  %".30" = bitcast [28 x i8]* @"str_5" to i8*
  %".31" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".31", i8* %".30")
  %".32" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %"i.1" = alloca i64
  store i64 0, i64* %"i.1"
  br label %"for_cond.2"
for_cond.2:
  %"for_curr.1" = load i64, i64* %"i.1"
  %"for_cond.3" = icmp slt i64 %"for_curr.1", 10
  br i1 %"for_cond.3", label %"for_body.1", label %"for_end.1"
for_body.1:
  %"arr_load.12" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i.1"
  %".36" = getelementptr i64, i64* %"arr_load.12", i64 %"i_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".36"
  %".37" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".37", i64 %"ptr_idx_load.1")
  %".38" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".38")
  br label %"for_inc.1"
for_inc.1:
  %"for_curr_inc.1" = load i64, i64* %"i.1"
  %"for_next.1" = add i64 %"for_curr_inc.1", 1
  store i64 %"for_next.1", i64* %"i.1"
  br label %"for_cond.2"
for_end.1:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [16 x i8] c"Array original:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [28 x i8] c"Array ordenado (QuickSort):\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"